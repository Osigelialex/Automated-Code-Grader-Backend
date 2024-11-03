from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from account.permissions import IsLecturerPermission, IsStudentPermission
from drf_spectacular.utils import extend_schema
from .service import CodeExecutionService
from .models import Assignment, Course, Submission
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.cache import cache
from django.utils import timezone
from ast import literal_eval
import time
from .service import CodeExecutionService
import logging, environ, logging
from .serializers import (
    AssignmentSerializer,
    AssignmentListSerializer,
    AssignmentDetailSerializer,
    AssignmentSubmissionSerializer,
    SubmissionSerializer,
    SubmissionDetailSerializer,
    AssignmentResultDataSerializer
)

logger = logging.getLogger(__name__)
env = environ.Env()

@extend_schema(tags=['assignment'])
class AssignmentCreateView(APIView):
    """
    API view to create an assignment
    """
    serializer_class = AssignmentSerializer
    permission_classes = [IsLecturerPermission]

    def post(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
            data = request.data.copy()
            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save(course=course)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Course.DoesNotExist:
            return Response({'message': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(tags=['assignment'])
class StudentAssignmentListView(generics.ListAPIView):
    """
    Endpoint to list assignments in a course
    """
    serializer_class = AssignmentListSerializer
    permission_classes = [IsStudentPermission]

    def get_queryset(self):
        return Assignment.objects.filter(course=self.kwargs['course_id'])


class AssignmentDetailView(generics.RetrieveAPIView):
    """
    Endpoint to retrieve an assignment by its id
    """
    serializer_class = AssignmentDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Assignment.objects.filter(id=self.kwargs['pk'])


class StudentSubmissionListView(APIView):
    """
    Retrieve all student submissions for an assignment
    """
    serializer_class = SubmissionSerializer

    def get(self, request, pk):
        submissions = Submission.objects.filter(student=request.user, assignment=pk)
        serializer = self.serializer_class(submissions, many=True)
        return Response(serializer.data)


class SubmissionDetailView(APIView):
    """
    Retrieve a submission by its id
    """
    serializer_class = SubmissionDetailSerializer

    def get(self, request, pk):
        submission = get_object_or_404(Submission, pk=pk)
        serializer = self.serializer_class(submission)
        return Response(serializer.data)


class AssignmentSubmissionView(APIView):
    """API view to receive and execute code submissions for an assignment."""
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [IsStudentPermission]
    MAX_RETRIES = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code_execution_client = CodeExecutionService()

    @transaction.atomic
    def post(self, request, pk):
        assignment = get_object_or_404(Assignment, pk=pk)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # verify that deadline has not been exceeded
        if assignment.deadline < timezone.now():
            return Response({ 'message': 'Deadline exceeded for this assignment' })

        # check if code is already in cache
        if cache.get(serializer.validated_data['code']):
            return Response(literal_eval(cache.get(serializer.validated_data['code'])), status=status.HTTP_200_OK)

        # Extract all the test cases created for the assignment and represent them
        # in an input-output format for easy validation by the code execution service
        test_cases = assignment.test_cases.values()
        test_cases = [{"input": tc["input"], "output": tc["output"]} for tc in test_cases]

        # retrieve tokens needed to get the assignment submission results from the judge0 API
        tokens = self.code_execution_client.submit_code(serializer.validated_data['code'], test_cases)

        # using the submission token to get the assignment submission result from judge0 API
        submission_results = self.code_execution_client.get_submission_result(tokens)

        # calculate final grade by using the number of passed test cases
        test_case_count = len(test_cases)
        accepted_count = 0
        for result in submission_results["submissions"]:
            if result["status"]["id"] == 3:
                accepted_count += 1

        score = (accepted_count / test_case_count) * assignment.max_score

        # include score in the response
        submission_results['score'] = score

        # store the submission results in cache for 5 minutes
        cache.set(serializer.validated_data['code'], repr(submission_results), 300)

        # store submission in database using retry logic
        for attempt in range(self.MAX_RETRIES):
            try:
                with transaction.atomic():
                    Submission.objects.create(
                        assignment=assignment,
                        student=request.user,
                        code=serializer.validated_data['code'],
                        score=score,
                        results=submission_results
                    )
                break
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed to save submission")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
                else:
                    return Response({ 'message': 'There was an issue saving your submission to the database, try again'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(submission_results, status=status.HTTP_200_OK)


class AssignmenResultData(generics.ListAPIView):
    """
    Retrieves the results of an assignment to the lecturer
    """
    permission_classes = [IsLecturerPermission]
    serializer_class = AssignmentResultDataSerializer

    def get_queryset(self):
        return Submission.objects.filter(assignment=self.kwargs['pk'], is_best=True)
