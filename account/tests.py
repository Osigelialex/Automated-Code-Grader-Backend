from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Student, Lecturer, CustomUser
from unittest.mock import patch

class AccountTests(APITestCase):
    """
    Test suite for account app
    """

    def test_student_register_successful(self):
        """Ensure a new student can be registered with valid data"""
        student_data = {
            'email': 'student@example.com',
            'first_name': 'john',
            'last_name': 'doe',
            'department': 'test department',
            'password': '@Securepassword123',
            'matric': '21/0513',
            'level': 100
        }

        url = reverse('student-register')

        with patch('account.email_manager.EmailManager.send_activation_email') as mock_send_activation_email:
            response = self.client.post(url, student_data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Student.objects.count(), 1)
            self.assertEqual(CustomUser.objects.count(), 1)
            
            created_user = CustomUser.objects.get(email=student_data['email'])
            self.assertEqual(created_user.first_name, 'john')
            
            created_student = Student.objects.get()
            self.assertEqual(created_student.matric, '21/0513')
            
            mock_send_activation_email.assert_called_once_with(created_user)

    def test_student_register_invalid_email(self):
        """Ensure registration fails with invalid email format"""
        invalid_student_data = {
            'email': 'invalid-email',
            'first_name': 'john',
            'last_name': 'doe',
            'department': 'test department',
            'password': '@Securepassword123',
            'matric': '21/0513',
            'level': 100
        }
        
        url = reverse('student-register')
        response = self.client.post(url, invalid_student_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Student.objects.count(), 0)
        self.assertEqual(CustomUser.objects.count(), 0)

    def test_lecturer_register_successful(self):
        """Ensure a new lecturer can be registered with valid data"""
        lecturer_data = {
            'email': 'lecturer@example.com',
            'first_name': 'jane',
            'last_name': 'doe',
            'department': 'test department',
            'password': '@Securepassword123',
            'staff_id': 'staff/123'
        }
        
        url = reverse('lecturer-register')

        with patch('account.email_manager.EmailManager.send_activation_email') as mock_send_activation_email:
            response = self.client.post(url, lecturer_data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Lecturer.objects.count(), 1)
            self.assertEqual(CustomUser.objects.count(), 1)
            
            created_user = CustomUser.objects.get(email=lecturer_data['email'])
            self.assertEqual(created_user.first_name, 'jane')
            
            created_lecturer = Lecturer.objects.get()
            self.assertEqual(created_lecturer.staff_id, 'staff/123')
            
            mock_send_activation_email.assert_called_once_with(created_user)

    def test_lecturer_register_invalid_email(self):
        """Ensure registration fails with invalid email format"""
        invalid_lecturer_data = {
            'email': 'invalid-email',
            'first_name': 'jane',
            'last_name': 'doe',
            'department': 'test department',
            'password': '@Securepassword123',
            'staff_id': 'staff/123'
        }
        
        url = reverse('lecturer-register')
        response = self.client.post(url, invalid_lecturer_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Lecturer.objects.count(), 0)
        self.assertEqual(CustomUser.objects.count(), 0)

    def test_password_reset_successful(self):
        """Ensure a user can reset their password"""
        # Create a user for password reset test
        user = CustomUser.objects.create_user(
            email='reset@example.com',
            first_name='reset',
            last_name='user',
            password='@Securepassword123',
            department='Computer Science'
        )
        
        url = reverse('reset-password')
        
        with patch('account.email_manager.EmailManager.send_password_reset_email') as mock_send_password_reset_email:
            response = self.client.post(url, {'email': user.email}, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            mock_send_password_reset_email.assert_called_once_with(user)

    def test_password_reset_nonexistent_user(self):
        """Ensure non-existent users cannot reset password"""
        url = reverse('reset-password')
        response = self.client.post(url, {'email': 'nonexistent@example.com'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_account_activation_successful(self):
        """Ensure an account activation email can be sent for a registered user"""
        # Create a user for activation test
        user = CustomUser.objects.create_user(
            email='activate@example.com',
            first_name='activate',
            last_name='user',
            password='@Securepassword123',
            department='Computer Science'
        )
        
        url = reverse('send-activation-token')
        
        with patch('account.email_manager.EmailManager.send_activation_email') as mock_send_activation_email:
            response = self.client.post(url, {'email': user.email}, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            mock_send_activation_email.assert_called_once_with(user)

    def test_account_activation_nonexistent_user(self):
        """Ensure activation email is not sent to non-existent accounts"""
        url = reverse('send-activation-token')
        response = self.client.post(url, {'email': 'notfound@example.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
