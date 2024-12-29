from rest_framework import serializers
from django.db import transaction
from .models import CustomUser, Lecturer, Student
from django.core.cache import cache
from django.contrib.auth import authenticate
import re


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

        self.create_profile(user=user, **validated_data)
        return user
    
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
    token = serializers.CharField(required=True)
    
    def validate(self, data):
        try:
            # Check if the token is valid by validating if it's still in cache 
            user_id = cache.get(data['token'])
            if not user_id:
                raise serializers.ValidationError('Token is invalid or expired')
            
            user = CustomUser.objects.get(pk=user_id)
            data['user'] = user
            return data
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError('Invalid user')


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
    
    def validate_token(self, token):
        user_id = cache.get(token)
        if not user_id:
            raise serializers.ValidationError('Invalid token')
        return user_id
    
    @transaction.atomic
    def create(self, validated_data):
        user = CustomUser.objects.select_for_update().filter(pk=validated_data['token']).first()
        if not user:
            raise serializers.ValidationError('Could not find user')

        user.set_password(validated_data['password'])
        user.save()
        return user


class LoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        user = authenticate(**data)
        if user:
            return user
        raise serializers.ValidationError('Invalid email or password')


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['matric', 'level']

class LecturerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecturer
        fields = ['staff_id']


class ProfileDetailSerializer(serializers.ModelSerializer):
    student_details = StudentProfileSerializer(source='student_profile', read_only=True)
    lecturer_details = LecturerProfileSerializer(source='lecturer_profile', read_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'department', 'role', 'student_details', 'lecturer_details']
        read_only_fields = ['email', 'role']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.role == CustomUser.Role.STUDENT:
            data.pop('lecturer_details', None)
        else:
            data.pop('student_details', None)
        return data