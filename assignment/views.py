from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from account.permissions import IsLecturerPermission, IsStudentPermission
from drf_spectacular.utils import extend_schema
from .service import CodeExecutionService
from .models import Assignment, Course, Submission, Feedback
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.cache import cache
from django.utils import timezone
from ast import literal_eval
import google.generativeai as genai
from .service import CodeExecutionService
import logging, environ, logging
from .serializers import (
    AssignmentSerializer,
    AssignmentListSerializer,
    AssignmentDetailSerializer,
    AssignmentSubmissionSerializer,
    SubmissionSerializer,
    SubmissionDetailSerializer,
    AssignmentResultDataSerializer,
    FeedbackRatingSerializer
)

logger = logging.getLogger(__name__)
env = environ.Env()

@extend_schema(tags=['assignment'])
class AssignmentCreateView(APIView):
    """
    API endpoint for creating an assignment for a course

    This view allows lecturers to create assignments for a course

    Attributes:
        permission_classes: list of permission classes that the view requires
        serializer_class: the serializer class to use for serializing the queryset
    Returns:
        201 CREATED: If the assignment was created successfully
        400 BAD REQUEST: If the request data is invalid
        404 NOT FOUND: If the course does not exist
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
    API endpoint for retrieving all assignments for a course by a student

    This view allows students to view all the assignments for a course

    Attributes:
        permission_classes: list of permission classes that the view requires
        serializer_class: the serializer class to use for serializing the queryset
    Returns:
        200 OK: List of assignments for the course
        400 BAD REQUEST: If the request data is invalid
        404 NOT FOUND: If the course does not exist
    """
    serializer_class = AssignmentListSerializer
    permission_classes = [IsStudentPermission]

    def get_queryset(self):
        return Assignment.objects.filter(course=self.kwargs['course_id'])


class AssignmentDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving an assignment by its id

    This view allows users to view the details of an assignment
    Attributes:
        permission_classes: list of permission classes that the view requires
        serializer_class: the serializer class to use for serializing the queryset
    Returns:
        200 OK: The assignment details
        404 NOT FOUND: If the assignment does not exist
        400 BAD REQUEST: If the request data is invalid
    """
    serializer_class = AssignmentDetailSerializer
    permission_classes = [IsAuthenticated]
    queryset = Assignment.objects.all()
    lookup_field = 'pk'


class StudentSubmissionListView(APIView):
    """
    API endpoint for retrieving all submissions for an assignment by a student

    This view allows students to view all the past submissions they have made for an assignment
    to enable them to track their progress and improve on their submissions

    Attributes:
        permission_classes: list of permission classes that the view requires
        serializer_class: the serializer class to use for serializing the queryset
    Returns:
        200 OK: List of submissions for the assignment
        400 BAD REQUEST: If the request data is invalid
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

    Attributes:
        permission_classes: list of permission classes that the view requires
        serializer_class: the serializer class to use for serializing the queryset
    Returns:
        200 OK: The submission details
        404 NOT FOUND: If the submission does not exist
        400 BAD REQUEST: If the request data is invalid
    """
    serializer_class = SubmissionDetailSerializer
    queryset = Submission.objects.all()
    lookup_field = 'pk'


class AssignmentSubmissionView(APIView):
    """
    API endpoint for making a code submission for an assignment

    This view handles the submission of code for an assignment by a student.
    It calls the code execution service to run the code against the test cases

    Attributes:
        permission_classes: list of permission classes that the view requires
        serializer_class: the serializer class to use for serializing the queryset
        MAX_RETRIES: the maximum number of retries to save the submission to the database
    Returns:
        200 OK: The submission results
        400 BAD REQUEST: If the request data is invalid
        500 INTERNAL SERVER ERROR: If there was an issue saving the submission to the database
    """
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [IsStudentPermission]
    throttle_scope = 'submission'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code_execution_client = CodeExecutionService()

    @transaction.atomic
    def post(self, request, pk):
        assignment = get_object_or_404(Assignment, pk=pk)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

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
            if result["status"] == "Accepted":
                accepted_count += 1

        score = (accepted_count / test_case_count) * assignment.max_score

        # include score in the response
        submission_results['score'] = score

        # store the submission results in cache for 5 minutes
        cache.set(serializer.validated_data['code'], repr(submission_results), 300)

        # store submission in database
        Submission.objects.create(
            assignment=assignment,
            student=request.user,
            code=serializer.validated_data['code'],
            score=score,
            results=submission_results
        )

        return Response(submission_results, status=status.HTTP_200_OK)


class AssignmentResultData(generics.ListAPIView):
    """
    API endpoint for retrieving aggregated assignment submissions for lecturers

    This view returns the best assignment submissions for each student who attempted the assignment
    this is useful for analysis and recording of assignment results

    Attributes:
        permission_classes: list of permission classes that the view requires
        serializer_class: the serializer class to use for serializing the queryset
    Returns:
        200 OK: List of best submissions for the assignment
        400 BAD REQUEST: If the request data is invalid
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

    Attributes:
        permission_classes: list of permission classes that the view requires
    Returns:
        200 OK: The feedback for the submission
        400 BAD REQUEST: If the request data is invalid
    """
    permission_classes = [IsStudentPermission]
    throttle_scope = 'feedback'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        genai.configure(api_key=env('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def post(self, request, submission_id):
        student_name = request.user.first_name
        submission = get_object_or_404(Submission, pk=submission_id)
        assignment = submission.assignment
        prompt = f"""
            Role: You are a programming coach providing feedback on student code.

            Assignment: {assignment.description}
            Programming Language: {assignment.programming_language}
            Student Code: {submission.code}
            Student Name: {student_name}

            Provide feedback addressing:
                1. Code correctness
                2. Code style and best practices
                3. Specific improvement suggestions
                4. Positive reinforcement for good practices
    
            Format feedback in a constructive, encouraging manner.
            Limit feedback to 20 words.
            Note: Do not give out the answers but rather guide the student
        """
        try:
            response = self.model.generate_content(prompt)
        except Exception as e:
            return Response({ 'error': 'CodeBuddy is unavailable right now' })

        # store response in database
        feedback = Feedback(
            submission=submission,
            content=response.text,
        )

        feedback.save()
        return Response({ 'feedback': response.text }, status=status.HTTP_200_OK)


class RateFeedbackView(APIView):
    """
    API endpoint for rating feedback generated for a students submission

    This view allows students to rate the feedback generated for their submission
    to enable the system to improve the quality of feedback generated

    Attributes:
        permission_classes: list of permission classes that the view requires
    Returns:
        200 OK: The feedback rating
        400 BAD REQUEST: If the request data is invalid
    """
    permission_classes = [IsStudentPermission]
    serializer_class = FeedbackRatingSerializer

    def post(self, request, feedback_id):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        feedback = get_object_or_404(Feedback, pk=feedback_id)
        feedback.rating = serializer.validated_data['rating']
        feedback.save()
        return Response({ 'message': 'Thank you! Feedback rated successfully' }, status=status.HTTP_200_OK)