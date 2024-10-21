from rest_framework import serializers
from django.db import transaction
from .models import CustomUser, Lecturer, Student
from .helpers import send_activation_email


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
        send_activation_email(user)
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
        send_activation_email(user)
        return lecturer
