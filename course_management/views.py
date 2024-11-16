from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from account.permissions import IsLecturerPermission, IsStudentPermission
from .serializers import CourseSerializer, JoinCourseSerializer, MessageSerializer, CourseListSerializer
from .models import Course
from drf_spectacular.utils import extend_schema


class CourseListCreateView(generics.ListCreateAPIView):
    """
    Create a new course or list exiting courses a user is teaching
    """
    permission_classes = [IsLecturerPermission]
    serializer_class = CourseSerializer

    def get_queryset(self):
        return Course.objects.filter(lecturer=self.request.user)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['lecturer'] = request.user
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class JoinCourseView(APIView):
    """
    View to allow students to join a course
    """
    permission_classes = [IsStudentPermission]
    serializer_class = JoinCourseSerializer

    @extend_schema(
            responses={
                200: MessageSerializer,
                404: MessageSerializer,
                400: MessageSerializer
            }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        course_join_code = serializer.validated_data['course_join_code']
        course = Course.objects.filter(course_join_code=course_join_code).first()
        if not course:
            return Response({'message': 'Course joining code invalid'}, status=status.HTTP_404_NOT_FOUND)

        if not course.course_open:
            return Response({'message': f'{course.course_code}-{course.title} is not open for joining'}, status=status.HTTP_400_BAD_REQUEST)

        if request.user in course.students.all():
            return Response({'message': f'You have already joined {course.course_code}-{course.title}'}, status=status.HTTP_400_BAD_REQUEST)

        course.students.add(request.user)
        return Response({'message': f'You have successfully joined {course.course_code}-{course.title}'}, status=status.HTTP_200_OK)


class StudentCourseListView(generics.ListAPIView):
    """
    View to list courses a student is enrolled in
    """
    permission_classes = [IsStudentPermission]
    serializer_class = CourseListSerializer

    def get_queryset(self):
        return Course.objects.filter(students=self.request.user)


class UnenrollView(APIView):
    """
    View to unenroll a student from a course
    """
    permission_classes = [IsStudentPermission]

    @extend_schema(
            responses={
                200: MessageSerializer,
                404: MessageSerializer,
                400: MessageSerializer
            }
    )
    def delete(self, request, pk):
        course = Course.objects.filter(id=pk).first()
        if not course:
            return Response({ 'message': 'Course not found' }, status=status.HTTP_404_NOT_FOUND)
        
        if request.user not in course.students.all():
            return Response({ 'message': f'You are not enrolled in {course.course_code}-{course.title}' }, status=status.HTTP_400_BAD_REQUEST)

        course.students.remove(request.user)
        return Response({ 'message': f'Unenrolled from {course.course_code}-{course.title}' })
