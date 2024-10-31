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
from django.utils import timezone
import time
from .service import CodeExecutionService
import logging, environ, logging
from .serializers import (
    AssignmentSerializer,
    AssignmentListSerializer,
    AssignmentDetailSerializer,
    AssignmentSubmissionSerializer,
    SubmissionDTOSerializer
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
        except Course.DoesNotExist:
            return Response({'message': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        data = request.data.copy()
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(course=course)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
    serializer_class = SubmissionDTOSerializer

    def get(self, request, pk):
        submissions = Submission.objects.filter(student=request.user, assignment=pk)
        serializer = self.serializer_class(submissions, many=True)
        return Response(serializer.data)


class AssignmentSubmissionView(APIView):
    """API view to receive and execute code submissions for an assignment."""
    serializer_class = AssignmentSubmissionSerializer
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

        # Extract all the test cases created for the assignment and represent them
        # in an input-output format for easy validation by the code execution service
        test_cases = assignment.test_cases.values()
        test_cases = [{"input": tc["input"], "output": tc["output"]} for tc in test_cases]

        # retrieve tokens needed to get the assignment submission results from
        # the judge0 API
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

        # verify if the new submission is the student's best submission
        previous_best = Submission.objects.filter(is_best=True).first()
        is_best_submission = score > previous_best.score
        if is_best_submission:
            previous_best.is_best = False
            previous_best.save()

        # include score in the response
        submission_results['score'] = score

        # store submission in database using retry logic
        for attempt in range(self.MAX_RETRIES):
            try:
                with transaction.atomic():
                    Submission.objects.create(
                        assignment=assignment,
                        student=request.user,
                        code=serializer.validated_data['code'],
                        is_best=is_best_submission,
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
