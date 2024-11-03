from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import Mock, patch
from django.contrib.auth import get_user_model
from .models import Assignment, Course, Submission, TestCase, ExampleTestCase

User = get_user_model()

class AssignmentViewsTest(APITestCase):
    def setUp(self):
        """Set up test data."""
        # Create users
        self.lecturer = User.objects.create_user(
            first_name='lecturer',
            last_name='doe',
            email='lecturer@example.com',
            password='testpass',
            role='LECTURER'
        )
        self.student = User.objects.create_user(
            first_name='student',
            last_name='doe',
            email='student@example.com',
            password='testpass',
            role='STUDENT'
        )

        # Create course
        self.course = Course.objects.create(
            title='Test Course',
            lecturer=self.lecturer,
            course_code='CSC401',
            course_units=3
        )
        
        # Create assignment
        self.assignment = Assignment.objects.create(
            title='Test Assignment',
            course=self.course,
            description='Test description',
            deadline=timezone.now() + timezone.timedelta(days=7),
            max_score=100,
            programming_language=Assignment.ProgrammingLanguage.PYTHON
        )

        # Create example test cases
        self.example_test_case = ExampleTestCase.objects.create(
            assignment=self.assignment,
            input="example_input",
            output="example_output"
        )

        # Create hidden test cases
        self.test_case = TestCase.objects.create(
            assignment=self.assignment,
            input="test_input",
            output="test_output"
        )

        # Create a submission
        self.submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.student,
            code='def solution(): return "Hello"',
            score=90.0,
            is_best=True,
            results={'submissions': [{'status': {'id': 3}}]}
        )

    def test_lecturer_can_create_assignment(self):
        """Test that a lecturer can create an assignment."""
        self.client.force_authenticate(user=self.lecturer)
        
        assignment_data = {
            'title': 'New Assignment',
            'description': 'Assignment description',
            'deadline': (timezone.now() + timezone.timedelta(days=7)).isoformat(),
            'max_score': 100,
            'programming_language': Assignment.ProgrammingLanguage.PYTHON,
            'example_test_cases': [
                {
                    'input': 'example_input',
                    'output': 'example_output'
                },
                {
                    'input': 'example_input',
                    'output': 'example_output'
                }
            ],
            'test_cases': [
                {
                    'input': 'test_input',
                    'output': 'test_output'
                },
                {
                    'input': 'test_input',
                    'output': 'test_output'
                },
                {
                    'input': 'test_input',
                    'output': 'test_output'
                }
            ]
        }
        
        url = reverse('create-assignment', kwargs={'course_id': self.course.id})
        response = self.client.post(url, assignment_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Assignment')
        self.assertEqual(response.data['programming_language'], Assignment.ProgrammingLanguage.PYTHON)
        
        # Verify test cases were created
        assignment = Assignment.objects.get(title='New Assignment')
        self.assertTrue(assignment.example_test_cases.exists())
        self.assertTrue(assignment.test_cases.exists())

    def test_non_lecturer_cannot_create_assignment(self):
        """Test that a non-lecturer cannot create an assignment."""
        self.client.force_authenticate(user=self.student)
        
        assignment_data = {
            'title': 'New Assignment',
            'description': 'Assignment description',
            'deadline': (timezone.now() + timezone.timedelta(days=7)).isoformat(),
            'max_score': 100,
            'programming_language': Assignment.ProgrammingLanguage.PYTHON,
            'example_test_cases': [{'input': 'test', 'output': 'expected'}],
            'test_cases': [{'input': 'test', 'output': 'expected'}]
        }
        
        url = reverse('create-assignment', kwargs={'course_id': self.course.id})
        response = self.client.post(url, assignment_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_can_list_assignments(self):
        """Test that a student can list assignments for a course."""
        self.client.force_authenticate(user=self.student)
        
        url = reverse('list-course-assignment', kwargs={'course_id': self.course.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        self.assertEqual(response.data[0]['title'], 'Test Assignment')
        self.assertTrue('example_test_cases' in response.data[0])
        self.assertFalse('test_cases' in response.data[0])  # Hidden test cases shouldn't be visible

    def test_assignment_detail_retrieval(self):
        """Test retrieving assignment details."""
        self.client.force_authenticate(user=self.student)
        
        url = reverse('assignment-detail', kwargs={'pk': self.assignment.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Assignment')
        self.assertEqual(response.data['programming_language'], Assignment.ProgrammingLanguage.PYTHON)
        self.assertTrue('example_test_cases' in response.data)

    @patch('assignment.service.CodeExecutionService')
    def test_successful_submission(self, mock_code_execution_service):
        """Test successful code submission for an assignment."""
        self.client.force_authenticate(user=self.student)
        
        # Mock CodeExecutionService
        mock_service_instance = Mock()
        mock_service_instance.submit_code.return_value = ['token1']
        mock_service_instance.get_submission_result.return_value = {
            'submissions': [
                {'status': {'id': 3}}
            ]
        }
        mock_code_execution_service.return_value = mock_service_instance
        
        submission_data = {
            'code': 'def solution():\n    return "Hello"'
        }
        
        url = reverse('assignment-submit', kwargs={'pk': self.assignment.id})
        response = self.client.post(url, submission_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('score', response.data)
        
        # Verify submission was created
        submission = Submission.objects.filter(
            assignment=self.assignment,
            student=self.student
        ).latest('submitted_at')
        self.assertIsNotNone(submission)
        self.assertEqual(submission.code, submission_data['code'])

    def test_submission_after_deadline(self):
        """Test submission after assignment deadline."""
        self.client.force_authenticate(user=self.student)
        
        # Set assignment deadline to past
        self.assignment.deadline = timezone.now() - timezone.timedelta(days=1)
        self.assignment.save()
        
        submission_data = {
            'code': 'def solution():\n    return "Hello"'
        }
        
        url = reverse('assignment-submit', kwargs={'pk': self.assignment.id})
        response = self.client.post(url, submission_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Deadline exceeded for this assignment')

    def test_student_submission_list(self):
        """Test retrieving student's submissions for an assignment."""
        self.client.force_authenticate(user=self.student)
        
        url = reverse('student-submissions', kwargs={'pk': self.assignment.id})
        response = self.client.get(url)
    
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        self.assertEqual(response.data[0]['score'], 90.0)
        self.assertTrue(response.data[0]['is_best'])

    def test_submission_detail_view(self):
        """Test retrieving submission details."""
        self.client.force_authenticate(user=self.student)
        
        url = reverse('submission-detail', kwargs={'pk': self.submission.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['score'], 90.0)
        self.assertEqual(response.data['student'], self.student.email)
        self.assertTrue('results' in response.data)

    def test_invalid_max_score(self):
        """Test assignment creation with invalid max score."""
        self.client.force_authenticate(user=self.lecturer)
        
        assignment_data = {
            'title': 'Invalid Score Assignment',
            'description': 'Test description',
            'deadline': (timezone.now() + timezone.timedelta(days=7)).isoformat(),
            'max_score': 101,  # Invalid: more than 100
            'programming_language': Assignment.ProgrammingLanguage.PYTHON
        }
        
        url = reverse('create-assignment', kwargs={'course_id': self.course.id})
        response = self.client.post(url, assignment_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access protected endpoints."""
        # Test assignment creation
        url = reverse('create-assignment', kwargs={'course_id': self.course.id})
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test assignment list
        url = reverse('list-course-assignment', kwargs={'course_id': self.course.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_assignment_result_data(self):
        """Test that the lecturer can view the results from all submissions in an assignment"""
        self.client.force_authenticate(user=self.lecturer)

        url = reverse('assignment-result', kwargs={'pk': self.assignment.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        self.assertEqual(response.data[0]['score'], 90.0)
        self.assertEqual(response.data[0]['code'], self.submission.code)
        self.assertEqual(response.data[0]['student']['first_name'], self.submission.student.first_name)
        self.assertEqual(response.data[0]['student']['last_name'], self.submission.student.last_name)
        self.assertEqual(response.data[0]['student']['department'], self.submission.student.department)
