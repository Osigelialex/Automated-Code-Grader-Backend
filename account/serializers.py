from rest_framework import serializers
from django.db import transaction
from rest_framework_simplejwt.tokens import Token
from .models import CustomUser, Lecturer, Student
from .email_manager import email_manager
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model


class StudentRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    department = serializers.CharField(max_length=100)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Student
        fields = ['email', 'first_name', 'last_name', 'department', 'password', 'matric', 'level']
    
    def validate_email(self, email):
        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError('Email Already exists')
        return email
    
    def validate_matric(self, matric):
        if Student.objects.filter(matric=matric).exists():
            raise serializers.ValidationError('Matric number already exists')
        return matric

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop('password')

        user = CustomUser.objects.create_user(
            email=validated_data.pop('email'),
            password=password,
            first_name=validated_data.pop('first_name'),
            last_name=validated_data.pop('last_name'),
            department=validated_data.pop('department'),
            role=CustomUser.Role.STUDENT
        )

        student = Student.objects.create(user=user, **validated_data)
        email_manager.send_activation_email(user)
        return student


class LecturerRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    department = serializers.CharField(max_length=100)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Lecturer
        fields = ['email', 'first_name', 'last_name', 'department', 'password', 'staff_id']

    def validate_email(self, email):
        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError('Email Already exists')
        return email

    def validate_staff_id(self, staff_id):
        if Lecturer.objects.filter(staff_id=staff_id).exists():
            raise serializers.ValidationError('Staff ID already exists')
        return staff_id

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop('password')

        user = CustomUser.objects.create_user(
            email=validated_data.pop('email'),
            password=password,
            first_name=validated_data.pop('first_name'),
            last_name=validated_data.pop('last_name'),
            department=validated_data.pop('department'),
            role=CustomUser.Role.LECTURER
        )

        lecturer = Lecturer.objects.create(user=user, **validated_data)
        email_manager.send_activation_email(user)
        return lecturer


class ForgottenPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        """Checks if the email exists in the database"""
        if not CustomUser.objects.exists(email=email):
            raise serializers.ValidationError('No account linked to provided email')
        return email


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
