from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from account.models import CustomUser, Lecturer
from django.urls import reverse


class TestCourseManagement(APITestCase):
    """
    Unittests for the Course app, restricted to users with the 'LECTURER' role
    """

    def setUp(self):
        self.client = APIClient()

        # Create a lecturer user
        self.lecturer_user = CustomUser.objects.create_user(
            email='lecturer@example.com',
            password='@SecurePass123',
            first_name='John',
            last_name='Doe',
            department='Computer Science',
            role='LECTURER'
        )
        self.lecturer_profile = Lecturer.objects.create(
            user=self.lecturer_user,
            staff_id='staff/001'
        )

        # Create a non-lecturer user
        self.student_user = CustomUser.objects.create_user(
            email='student@example.com',
            password='@SecurePass123',
            first_name='Jane',
            last_name='Smith',
            department='Computer Science',
            role='STUDENT'
        )

    def test_course_creation_by_lecturer(self):
        """Ensure a lecturer can create a course"""
        url = reverse('course-list-create')
        data = {
            'title': 'Test Course',
            'description': 'Test course description',
            'course_code': 'CSC401',
            'course_units': 3,
        }

        # Authenticate as lecturer
        self.client.force_authenticate(user=self.lecturer_user)

        # Attempt to create the course
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], data['title'])
        self.assertEqual(response.data['description'], data['description'])

    def test_course_creation_by_non_lecturer(self):
        """Ensure a non-lecturer cannot create a course"""
        url = reverse('course-list-create')
        data = {
            'title': 'Unauthorized Course',
            'description': 'This should not be created',
            'course_code': 'CSC999',
            'course_units': 2,
        }

        # Authenticate as a student user
        self.client.force_authenticate(user=self.student_user)

        # Attempt to create the course
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
