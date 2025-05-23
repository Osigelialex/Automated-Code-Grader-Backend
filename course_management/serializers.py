from rest_framework import serializers
from .models import Course
import re
from account.models import CustomUser


class LecturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'department']


class CourseListSerializer(serializers.ModelSerializer):
    lecturer = LecturerSerializer()

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'course_code', 'course_units', 'lecturer', 'course_join_code']


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'course_code', 'course_units', 'course_join_code']
        read_only_fields = ['course_join_code', 'id', 'lecturer']

    def validate_course_units(self, value):
        if value < 1:
            raise serializers.ValidationError('Course units must be greater than 0')
        return value
    
    def validate_course_code(self, course_code):
        pattern = r'^CSC\d{3}$'
        if not re.match(pattern, course_code):
            raise serializers.ValidationError('Course code must follow the format CSCxxx')
        return course_code


class JoinCourseSerializer(serializers.Serializer):
    course_join_code = serializers.CharField()


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()
