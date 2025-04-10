from rest_framework import serializers
from django.utils import timezone
from .models import Feedback, Assignment, TestCase, Submission, Feedback
from course_management.serializers import CourseSerializer
from .service import code_execution_service
from account.models import CustomUser
import logging

logger = logging.getLogger(__name__)


class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = ['input', 'output', 'is_hidden']

    def validate_input(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError('Invalid input data type')
        return value


class AssignmentSerializer(serializers.ModelSerializer):
    test_cases = TestCaseSerializer(many=True)

    def validate_deadline(self, value):
        if value < timezone.now():
            raise serializers.ValidationError('Deadline must be in the future')
        return value
    
    def validate_max_score(self, value):
        if value <= 0:
            raise serializers.ValidationError('Max score must be greater than 0')
        return value
    
    def validate_language_id(self, language_id):
        if not code_execution_service.validate_language(language_id):
            raise serializers.ValidationError('Language id is invalid')
        return language_id
    
    def validate(self, data):
        test_cases = data.get('test_cases', [])

        if len(test_cases) < 3:
            raise serializers.ValidationError('At least three test case must be provided')

        # at least 2 hidden test cases should be created
        if len([test_case for test_case in test_cases if test_case.get('is_hidden', True)]) < 2:
            raise serializers.ValidationError('At least two hidden test case must be provided')

        return data

    def create(self, validated_data):
        test_cases_data = validated_data.pop('test_cases')
        assignment = Assignment.objects.create(**validated_data)

        # store test cases in db
        TestCase.objects.bulk_create([
            TestCase(assignment=assignment, **test_case_data)
            for test_case_data in test_cases_data
        ])

        return assignment

    class Meta:
        model = Assignment
        fields = ['title', 'description', 'deadline',
                  'max_score', 'language_id', 'programming_language',
                  'course', 'test_cases']
        read_only_fields = ['course']


class AssignmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'title', 'description', 'deadline',
                  'max_score', 'programming_language', 'language_id', 'is_draft',
                'created_at', 'updated_at']
        ordering = ['-created_at']


class AssignmentDetailSerializer(serializers.ModelSerializer):
    test_cases = TestCaseSerializer(many=True)
    course = CourseSerializer()

    class Meta:
        model = Assignment
        fields = '__all__'
        ordering = ['-created_at']


class AssignmentSubmissionSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['id', 'code', 'score', 'is_best', 'submitted_at']


class SubmissionDetailSerializer(serializers.ModelSerializer):
    assignment = AssignmentSerializer()
    student = serializers.StringRelatedField()

    class Meta:
        model = Submission
        fields = '__all__'
        ordering = ['-submitted_at']


class StudentSerializer(serializers.ModelSerializer):
    matric = serializers.CharField(source='student_profile.matric')

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'department', 'matric']


class AssignmentResultDataSerializer(serializers.ModelSerializer):
    student = StudentSerializer()

    class Meta:
        model = Submission
        fields = ['score', 'code', 'submitted_at', 'student']


class FeedbackRatingSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Feedback
        fields = ['rating']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('Rating must be between 1 and 5')
        return value


class FeedbackListSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source='submission.code')
    score = serializers.CharField(source='submission.score')

    class Meta:
        model = Feedback
        fields = ['id', 'content', 'rating', 'code', 'score']
        ordering = ['-created_at']


class ProgrammingLanguageSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

    class Meta:
        fields = ['id', 'name']