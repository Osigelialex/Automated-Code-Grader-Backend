from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from django_filters import rest_framework as filters
from account.permissions import IsLecturerPermission, IsStudentPermission
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Assignment, Course, Submission, Feedback, TestCase
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.cache import cache
from django.utils import timezone
from .filters import AssignmentFilter
import google.generativeai as genai
from .service import code_execution_service
import logging, environ, logging, json
from .serializers import (
    AssignmentSerializer,
    AssignmentListSerializer,
    AssignmentDetailSerializer,
    AssignmentSubmissionSerializer,
    SubmissionSerializer,
    SubmissionDetailSerializer,
    AssignmentResultDataSerializer,
    FeedbackRatingSerializer,
    FeedbackListSerializer,
    ProgrammingLanguageSerializer,
)

logger = logging.getLogger(__name__)
env = environ.Env()

@extend_schema(tags=['assignments'])
class AssignmentCreateView(APIView):
    """
    API endpoint for creating an assignment for a course

    This view allows lecturers to create assignments for a course
    """
    serializer_class = AssignmentSerializer
    permission_classes = [IsLecturerPermission]

    def post(self, request, pk):
        try:
            course = Course.objects.get(id=pk)
            data = request.data.copy()
            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save(course=course)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Course.DoesNotExist:
            return Response({'message': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)


class PublishAssignmentView(APIView):
    """
    API endpoint for publishing an assignment

    This view allows lecturers to publish an assignment to make it available to students
    """
    permission_classes = [IsLecturerPermission]

    def patch(self, request, pk):
        assignment = get_object_or_404(Assignment, pk=pk)
        assignment.is_draft = False
        assignment.save()
        return Response({ 'message': 'Assignment published successfully' }, status=status.HTTP_200_OK)


@extend_schema(
    tags=['assignments'],
    parameters=[
        OpenApiParameter(name='is_draft', description='Filter assignments by draft status', required=False, type=bool)
    ]
)
class AssignmentListView(generics.ListAPIView):
    """
    API endpoint for retrieving all assignments for a course

    This view allows users to view all the assignments for a course
    """
    serializer_class = AssignmentListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = AssignmentFilter

    def get_queryset(self):
        return Assignment.objects.filter(course=self.kwargs['pk'])


class AssignmentDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving an assignment by its id

    This view allows users to view the details of an assignment
    """
    serializer_class = AssignmentDetailSerializer
    permission_classes = [IsAuthenticated]
    queryset = Assignment.objects.all()
    lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        assignment = self.get_object()
        visible_test_cases = TestCase.objects.filter(assignment=assignment, is_hidden=False)
        assignment_data = self.get_serializer(assignment).data
        assignment_data['test_cases'] = list(visible_test_cases.values('id', 'input', 'output'))
        return Response(assignment_data)


class StudentSubmissionListView(APIView):
    """
    API endpoint for retrieving all submissions for an assignment by a student

    This view allows students to view all the past submissions they have made for an assignment
    to enable them to track their progress and improve on their submissions
    """
    serializer_class = SubmissionSerializer
    permission_classes = [IsStudentPermission]

    def get(self, request, pk):
        submissions = Submission.objects.filter(student=request.user, assignment=pk)
        serializer = self.serializer_class(submissions, many=True)
        return Response(serializer.data)


class SubmissionDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a submission by its id

    This view allows users to view the details of a submission made for an assignment
    """
    serializer_class = SubmissionDetailSerializer
    queryset = Submission.objects.all()
    lookup_field = 'pk'


class AssignmentSubmissionView(APIView):
    """
    API endpoint for making a code submission for an assignment

    This view handles the submission of code for an assignment by a student.
    It calls the code execution service to run the code against the test cases
    """
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [IsStudentPermission]
    throttle_scope = 'submission'

    @transaction.atomic
    def post(self, request, pk):
        assignment = get_object_or_404(Assignment, pk=pk)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        if assignment.deadline < timezone.now():
            return Response({ 'message': 'Deadline exceeded for this assignment' })

        # check if code is already in cache
        if cache.get(serializer.validated_data['code']):
            return Response(json.loads(cache.get(serializer.validated_data['code'])), status=status.HTTP_200_OK)

        # Extract all the test cases created for the assignment and represent them
        # in an input-output format for easy validation by the code execution service
        test_cases = assignment.test_cases.values()
        test_cases = [{"input": tc["input"], "output": tc["output"]} for tc in test_cases]

        # retrieve tokens needed to get the assignment submission results from the judge0 API
        try:
            tokens = code_execution_service.submit_code(serializer.validated_data['code'], assignment.language_id,  test_cases)
        except Exception as e:
            return Response({ 'message': 'Could not execute code, please try again' }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # using the submission token to get the assignment submission result from judge0 API
        submission_results = code_execution_service.get_submission_result(tokens)

        # calculate final grade by using the number of passed test cases
        test_case_count = len(test_cases)
        accepted_count = 0
        for result in submission_results["submission_result"]:
            if result["status"] == "Accepted":
                accepted_count += 1

        score = (accepted_count / test_case_count) * assignment.max_score

        # include score in the response
        submission_results['score'] = score

        # store submission in database
        submission = Submission.objects.create(
            assignment=assignment,
            student=request.user,
            code=serializer.validated_data['code'],
            score=score,
            results=submission_results
        )

        # Convert UUID to string before adding to submission_results
        submission_results['submission_id'] = str(submission.id)

        cache_data = {
            'submission_id': str(submission.id),
            'score': score,
            'submission_result': submission_results['submission_result']
        }

        # store the submission results in cache for 10 minutes
        cache.set(serializer.validated_data['code'], json.dumps(cache_data), 600)

        return Response(submission_results, status=status.HTTP_200_OK)


class AssignmentResultData(generics.ListAPIView):
    """
    API endpoint for retrieving aggregated assignment submissions for lecturers

    This view returns the best assignment submissions for each student who attempted the assignment
    this is useful for analysis and recording of assignment results
    """
    permission_classes = [IsLecturerPermission]
    serializer_class = AssignmentResultDataSerializer

    def get_queryset(self):
        return Submission.objects.filter(assignment=self.kwargs['pk'], is_best=True)


class FeedbackGenerationView(APIView):
    """
    API endpoint for generating personalized feedback for a students submission

    This view takes in the submission results and generates personalized feedback for the student
    based on the test cases that were passed and failed
    """
    permission_classes = [IsStudentPermission]
    throttle_scope = 'feedback'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        genai.configure(api_key=env('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def post(self, request, pk):
        if cache.get(f'feedback_{pk}'):
            return Response({ 'feedback': cache.get(f'feedback_{pk}') }, status=status.HTTP_200_OK)

        student_name = request.user.first_name
        submission = get_object_or_404(Submission, pk=pk)
        assignment = submission.assignment
        prompt = f"""
        Role: Programming Assistant providing constructive student code feedback

        Key Objectives:
        - Evaluate code correctness without giving direct solutions
        - Assess code style and best practices
        - Provide actionable improvement suggestions
        - Offer positive reinforcement

        Feedback Principles:
        - Constructive and encouraging tone
        - Preserve student's problem-solving ownership
        - Keep feedback concise, focused and very short

        Assignment Description: {assignment.description}
        Programming Language: {assignment.programming_language}
        Student Code Submission: {submission.code}
        Student Name: {student_name}
        """
        try:
            response = self.model.generate_content(prompt)
        except Exception as e:
            return Response({ 'error': 'CheckMate AI is unavailable right now' })

        # store response in database
        feedback = Feedback(
            submission=submission,
            content=response.text,
        )

        feedback.save()

        # cache feedback in redis for 30 minutes
        cache.set(f'feedback_{submission.id}', response.text, 1800)
        return Response({ 'feedback': response.text }, status=status.HTTP_200_OK)


class RateFeedbackView(APIView):
    """
    API endpoint for rating feedback generated for a students submission

    This view allows students to rate the feedback generated for their submission
    to enable the system to improve the quality of feedback generated
    """
    permission_classes = [IsStudentPermission]
    serializer_class = FeedbackRatingSerializer

    def post(self, request, pk):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        feedback = get_object_or_404(Feedback, pk=pk)
        feedback.rating = serializer.validated_data['rating']
        feedback.save()
        return Response({ 'message': 'Thank you! Feedback rated successfully' }, status=status.HTTP_200_OK)


class FeedbackListView(generics.ListAPIView):
    """
    API endpoint for retrieving all feedbacks

    This view lists all the feedbacks for analysis purposes
    """
    serializer_class = FeedbackListSerializer
    queryset = Feedback.objects.all()


class RetrieveProgrammingLanguages(generics.ListAPIView):
    """
    Get a list of available programming languages
    """
    serializer_class = ProgrammingLanguageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            languages = code_execution_service.get_available_languages()
            return languages
        except Exception as e:
            return Response({ 'error': 'Error fetching programming languages' }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
