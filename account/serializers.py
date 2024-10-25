from rest_framework import serializers
from django.db import transaction
from .models import CustomUser, Lecturer, Student, Token
from .email_manager import email_manager
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
import re
import base64


class BaseRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    department = serializers.CharField(max_length=100)
    password = serializers.CharField(write_only=True)

    def validate_email(self, email):
        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError('Email Already exists')
        return email
    
    def validate_password(self, password):
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>])[A-Za-z\d!@#$%^&*(),.?\":{}|<>]{8,}$"

        if not re.match(pattern, password):
            raise serializers.ValidationError(
                'Password must contain at least 8 characters, one uppercase letter, one lowercase letter, one digit and one special character'
                )
        
        return password

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop('password')

        user = CustomUser.objects.create_user(
            email=validated_data.pop('email'),
            password=password,
            first_name=validated_data.pop('first_name'),
            last_name=validated_data.pop('last_name'),
            department=validated_data.pop('department'),
            role=self.get_role()
        )

        profile = self.create_profile(user=user, **validated_data)
        email_manager.send_activation_email(user)
        return profile
    
    def create_profile(self, user, validated_data):
        raise NotImplementedError('Subclass must implement create_profile()')
    
    def get_role(self):
        raise NotImplementedError('Subclass must implement get_role()')


class StudentRegistrationSerializer(BaseRegisterSerializer):
    class Meta:
        model = Student
        fields = ['email', 'first_name', 'last_name', 'department', 'password', 'matric', 'level']
    
    def validate_matric(self, matric):
        if Student.objects.filter(matric=matric).exists():
            raise serializers.ValidationError('Matric number already exists')
        return matric

    def create_profile(self, user, **validated_data):
        return Student.objects.create(user=user, **validated_data)
    
    def get_role(self):
        return CustomUser.Role.STUDENT


class LecturerRegistrationSerializer(BaseRegisterSerializer):
    class Meta:
        model = Lecturer
        fields = ['email', 'first_name', 'last_name', 'department', 'password', 'staff_id']

    def validate_staff_id(self, staff_id):
        if Lecturer.objects.filter(staff_id=staff_id).exists():
            raise serializers.ValidationError('Staff ID already exists')
        return staff_id

    def create_profile(self, user, **validated_data):
        return Lecturer.objects.create(user=user, **validated_data)

    def get_role(self):
        return CustomUser.Role.LECTURER


class ForgottenPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ActivateAccountSerializer(serializers.Serializer):
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    
    def validate(self, data):
        try:
            user_id = base64.b64decode(data['uid']).decode('utf-8')
            user = CustomUser.objects.get(pk=user_id)
            token = Token.objects.get(key=data['token'])

            if token.is_used or token.is_expired():
                raise serializers.ValidationError('Token is invalid or expired')
            
            data['user'] = user
            data['token'] = token
            return data
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError('Invalid user')
        except Token.DoesNotExist:
            raise serializers.ValidationError('Invalid token')
        except (TypeError, ValueError, OverflowError):
            raise serializers.ValidationError('Invalid uid')


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate_password(self, password):
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>])[A-Za-z\d!@#$%^&*(),.?\":{}|<>]{8,}$"

        if not re.match(pattern, password):
            raise serializers.ValidationError(
                'Password must contain at least 8 characters, one uppercase letter, one lowercase letter, one digit and one special character'
                )
        
        return password
    
    @transaction.atomic
    def create(self, validated_data):
        try:
            token = Token.objects.get(key=validated_data['token'])
            user = token.user
            user.set_password(validated_data['password'])
            token.is_used = True
            user.save()
            token.save()
            return user
        except Token.DoesNotExist:
            raise serializers.ValidationError('Invalid token')


class SendActivationTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """
        Validates email and returns user if exists
        """
        try:
            user = CustomUser.objects.get(email=value)
            return value
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError('No account linked to provided email')

    def validate(self, attrs):
        """
        Returns validated data with user instance
        """
        user = CustomUser.objects.get(email=attrs['email'])
        if user.is_active:
            raise serializers.ValidationError('Account is already activated')

        attrs['user'] = user
        return attrs


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        credentials = {
            # Retrieve only the username field from paylod
            self.username_field: attrs.get(self.username_field),
            'password': attrs.get('password')
        }

        # Get the auth user model used for the django app
        User = get_user_model()
        
        try:
            user = User.objects.get(**{self.username_field: credentials[self.username_field]})
            
            # Check if user is active
            if not user.is_active:
                raise serializers.ValidationError(
                    {'detail': 'Account is not active.'},
                    code='inactive_account'
                )
                
            # If user is active, proceed with normal token generation
            return super().validate(attrs)

        except User.DoesNotExist:
            # We don't want to reveal whether a user exists or not
            # So we use the same error message as invalid credentials
            raise serializers.ValidationError(
                {'detail': 'No active account found with the given credentials'},
                code='authorization'
            )
