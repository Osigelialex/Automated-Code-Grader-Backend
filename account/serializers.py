from rest_framework import serializers
from django.db import transaction
from .models import CustomUser, Lecturer, Student, Token
from .email_manager import email_manager
from django.contrib.auth import authenticate
import re, base64


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


class LoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError('Invalid email or password')
