from rest_framework import serializers
from django.utils import timezone
from .models import Assignment, TestCase, ExampleTestCase, Submission
from course_management.serializers import CourseSerializer
import logging

logger = logging.getLogger(__name__)


class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = ['input', 'output']

    def validate_input(self, value):
        if not isinstance(value, (list, int, str, dict, float, bool)):
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
