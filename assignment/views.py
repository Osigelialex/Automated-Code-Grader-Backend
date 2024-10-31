from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from account.permissions import IsLecturerPermission, IsStudentPermission
from drf_spectacular.utils import extend_schema
from .service import CodeExecutionService
from .models import Assignment, Course, Submission
from django.shortcuts import get_object_or_404
from .service import CodeExecutionService
import logging, environ, logging
from .serializers import (
    AssignmentSerializer,
    AssignmentListSerializer,
    AssignmentDetailSerializer,
    AssignmentSubmissionSerializer
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


class AssignmentSubmissionView(APIView):
    """API view to receive and execute code submissions for an assignment."""
    serializer_class = AssignmentSubmissionSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code_execution_client = CodeExecutionService()

    def post(self, request, pk):
        assignment = get_object_or_404(Assignment, pk=pk)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        test_cases = assignment.test_cases.values()
        test_cases = [{"input": tc["input"], "output": tc["output"]} for tc in test_cases]

        tokens = self.code_execution_client.submit_code(serializer.validated_data['code'], test_cases)
        submission_results = self.code_execution_client.get_submission_result(tokens)

        # calculate score
        test_case_count = len(test_cases)
        accepted_count = 0
        for result in submission_results["submissions"]:
            if result["status"]["id"] == 3:
                accepted_count += 1

        score = (accepted_count / test_case_count) * assignment.max_score
        submission_results = {
            "score": score,
            "results": submission_results
        }

        Submission.objects.create(
            assignment=assignment,
            student=request.user,
            code=serializer.validated_data['code'],
            score=score,
            results=submission_results
        )

        return Response(submission_results, status=status.HTTP_200_OK)
