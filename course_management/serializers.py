from rest_framework import serializers
from .models import Course
import re


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['title', 'description', 'course_code', 'course_units', 'lecturer', 'course_join_code']
        read_only_fields = ['course_join_code']

    def validate_course_units(self, value):
        if value < 1:
            raise serializers.ValidationError('Course units must be greater than 0')
        return value
    
    def validate_course_code(self, course_code):
        pattern = '^CSC\d{3}$'
        if not re.match(pattern, course_code):
            raise serializers.ValidationError('Course code must follow the format CSCxxx')
        return course_code
