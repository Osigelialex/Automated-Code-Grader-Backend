from rest_framework import serializers
from django.utils import timezone
from .models import Feedback, Assignment, TestCase, ExampleTestCase, Submission, Feedback
from course_management.serializers import CourseSerializer
from account.models import CustomUser
import logging

logger = logging.getLogger(__name__)


class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = ['input', 'output']

    def validate_input(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError('Invalid input data type')
        return value


class ExampleTestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExampleTestCase
        fields = ['input', 'output']


class AssignmentSerializer(serializers.ModelSerializer):
    example_test_cases = ExampleTestCaseSerializer(many=True)
    test_cases = TestCaseSerializer(many=True)

    def validate_deadline(self, value):
        if value < timezone.now():
            raise serializers.ValidationError('Deadline must be in the future')
        return value
    
    def validate_max_score(self, value):
        if value <= 0:
            raise serializers.ValidationError('Max score must be greater than 0')
        return value

    def validate_programming_language(self, value):
        if value not in ['Python', 'Java', 'C++']:
            raise serializers.ValidationError('Invalid programming language')
        return value
    
    def validate(self, data):
        test_cases = data.get('test_cases', [])
        example_test_cases = data.get('example_test_cases', [])

        if len(test_cases) < 3:
            raise serializers.ValidationError('At least three test case must be provided')

        if len(example_test_cases) < 2:
            raise serializers.ValidationError('At least two example test case must be provided')
        return data

    def create(self, validated_data):
        test_cases_data = validated_data.pop('test_cases')
        example_test_cases = validated_data.pop('example_test_cases')
        assignment = Assignment.objects.create(**validated_data)

        # store test cases in db
        TestCase.objects.bulk_create([
            TestCase(assignment=assignment, **test_case_data)
            for test_case_data in test_cases_data
        ])

        # store example test cases in db
        ExampleTestCase.objects.bulk_create([
            ExampleTestCase(assignment=assignment, **example_test_case)
            for example_test_case in example_test_cases
        ])

        return assignment

    class Meta:
        model = Assignment
        fields = ['title', 'description', 'deadline',
                  'max_score', 'programming_language',
                  'course', 'example_test_cases', 'test_cases']
        read_only_fields = ['course']


class AssignmentListSerializer(serializers.ModelSerializer):
    example_test_cases = ExampleTestCaseSerializer(many=True)

    class Meta:
        model = Assignment
        fields = '__all__'
        ordering = ['-created_at']


class AssignmentDetailSerializer(serializers.ModelSerializer):
    test_cases = TestCaseSerializer(many=True)
    example_test_cases = ExampleTestCaseSerializer(many=True)
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
        fields = ['content', 'rating', 'code', 'score']
        ordering = ['-created_at']