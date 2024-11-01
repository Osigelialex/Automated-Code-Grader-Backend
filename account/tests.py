from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Student, Lecturer, CustomUser
from unittest.mock import patch


class AccountTests(APITestCase):
    """
    Test module for account app
    """
    @patch('account.email_manager.EmailManager.send_activation_email')
    def test_student_register(self, mock_send_activation_email):
        """
        Ensure we can register a new student
        """
        url = reverse('student-register')
        data = {
            'email': 'student@example.com',
            'first_name': 'john',
            'last_name': 'doe',
            'department': 'test department',
            'password': '@Securepassword123',
            'matric': '21/0513',
            'level': 100
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(), 1)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(CustomUser.objects.get().first_name, 'john')
        self.assertEqual(Student.objects.get().matric, '21/0513')
        mock_send_activation_email.assert_called_once_with(CustomUser.objects.get())

    @patch('account.email_manager.EmailManager.send_activation_email')
    def test_lecturer_register(self, mock_send_activation_email):
        """
        Ensure we can register a new lecturer
        """
        url = reverse('lecturer-register')
        data = {
            'email': 'lecturer@example.com',
            'first_name': 'jane',
            'last_name': 'doe',
            'department': 'test department',
            'password': '@Securepassword123',
            'staff_id': 'staff/123'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lecturer.objects.count(), 1)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(CustomUser.objects.get().first_name, 'jane')
        self.assertEqual(Lecturer.objects.get().staff_id, 'staff/123')
        mock_send_activation_email.assert_called_once_with(CustomUser.objects.get())

    def test_lecturer_register_invalid_data(self):
        """
        Ensure we can't register a new lecturer with invalid data
        """
        url = reverse('lecturer-register')
        data = {
            'email': 'invalid-email',
            'first_name': 'jane',
            'last_name': 'doe',
            'department': 'test department',
            'password': 'invalidpassword'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Lecturer.objects.count(), 0)
        self.assertEqual(CustomUser.objects.count(), 0)

    def test_student_register_invalid_data(self):
        """
        Ensure we can't register a new student with invalid data
        """
        url = reverse('student-register')
        data = {
            'email': 'invalid-email',
            'first_name': 'jane',
            'last_name': 'doe',
            'department': 'test department',
            'password': 'invalidpassword'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Lecturer.objects.count(), 0)
        self.assertEqual(CustomUser.objects.count(), 0)

    @patch('account.email_manager.EmailManager.send_password_reset_email')
    def test_password_reset(self, mock_send_password_reset_email):
        """
        Ensure we can reset a user's password
        """
        user = CustomUser.objects.create_user(
            email='student@example.com',
            first_name='john',
            last_name='doe',
            password='@Securepassword123',
            department='Computer Science',
            role='STUDENT'
        )

        Student.objects.create(
            matric='21/0603',
            level=400,
            user=user
        )

        url = reverse('reset-password')
        data = {'email': user.email}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send_password_reset_email.assert_called_once_with(CustomUser.objects.get())

    def test_password_reset_wrong_details(self):
        """
        Ensure we can't reset the password of a user that does not exist
        """
        url = reverse('reset-password')
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('account.email_manager.EmailManager.send_activation_email')
    def test_account_activation(self, mock_send_activation_email):
        """
        Ensure we can activate an account
        """
        user = CustomUser.objects.create_user(
            email='john@example.com',
            first_name='john',
            last_name='doe',
            password='@Securepassword123',
            department='Computer Science',
            role='STUDENT'
        )

        Student.objects.create(
            matric='21/0603',
            level=400,
            user=user
        )

        url = reverse('send-activation-token')
        data = {'email': user.email}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send_activation_email.assert_called_once_with(CustomUser.objects.get())
    
    def test_account_activation_wrong_details(self):
        """
        Ensure we can not send activation emails to non-existent accounts
        """
        url = reverse('send-activation-token')
        data = {'email': 'notfound@example.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
