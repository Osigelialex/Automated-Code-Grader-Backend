from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from account.permissions import IsLecturerPermission, IsStudentPermission
from drf_spectacular.utils import extend_schema
from .models import Assignment, Course, Submission
from django.shortcuts import get_object_or_404
from .service import CodeExecutionService
import logging
from .serializers import (
    AssignmentSerializer,
    AssignmentListSerializer,
    AssignmentDetailSerializer,
    AssignmentSubmissionSerializer
)

logger = logging.getLogger(__name__)

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


class AssignmentSubmitAPIView(APIView):
    """API view to submit an assignment with rate limiting and validation."""
    serializer_class = AssignmentSubmissionSerializer
    
    def post(self, request, pk=None):
        """Submit and execute code for an assignment with additional security measures."""
        try:
            assignment = get_object_or_404(Assignment, pk=pk)
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            code = request.data['code']

            # Execute code
            execution_service = CodeExecutionService()
            results = execution_service.execute_code(
                code=code,
                language=assignment.programming_language,
                test_cases=list(assignment.test_cases.all().values('input', 'output'))
            )

            score = (results['passed_count'] / results['total_tests']) * assignment.max_score

            # Save submission with retry logic
            for _ in range(3):
                try:
                    submission = Submission.objects.create(
                        assignment=assignment,
                        student=request.user,
                        code=code,
                        score=score,
                        results=results
                    )
                    break
                except Exception as e:
                    logger.error(f"Error saving submission: {str(e)}")
                    continue
            else:
                raise Exception("Failed to save submission after multiple attempts")

            return Response({
                'submission_id': submission.id,
                'score': score,
                'results': results
            })

        except Exception as e:
            logger.error(f"Error processing submission: {str(e)}")
            return Response(
                {'error': 'An error occurred processing your submission'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
