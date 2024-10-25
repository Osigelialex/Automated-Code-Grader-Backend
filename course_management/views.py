from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from account.permissions import IsLecturerPermission, IsStudentPermission
from .serializers import CourseSerializer
from .models import Course


class CourseCreationView(generics.CreateAPIView):
    """
    View to create a course
    """
    permission_classes = [IsLecturerPermission]
    serializer_class = CourseSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['lecturer'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class JoinCourseView(APIView):
    """
    View to allow students to join a course
    """
    permission_classes = [IsStudentPermission]

    def post(self, request, *args, **kwargs):
        course_join_code = request.data.get('course_join_code')
        course = Course.objects.filter(course_join_code=course_join_code).first()
        if not course:
            return Response({'message': 'Course joining code invalid'}, status=status.HTTP_404_NOT_FOUND)

        if not course.course_open:
            return Response({'message': f'{course.course_code}-{course.title} is not open for joining'}, status=status.HTTP_400_BAD_REQUEST)

        if request.user in course.students.all():
            return Response({'message': f'You have already joined {course.course_code}-{course.title}'}, status=status.HTTP_400_BAD_REQUEST)

        course.students.add(request.user)
        return Response({'message': f'You have successfully joined {course.course_code}-{course.title}'}, status=status.HTTP_200_OK)
