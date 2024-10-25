import base64
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser
from django.db import transaction
from .email_manager import email_manager
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    StudentRegistrationSerializer,
    LecturerRegistrationSerializer,
    ForgottenPasswordSerializer,
    MyTokenObtainPairSerializer,
    SendActivationTokenSerializer,
    ResetPasswordSerializer,
    ActivateAccountSerializer
    )


class BaseRegisterView(generics.CreateAPIView):
    """
    Base class for registering users into the system
    """
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Please check your email to verify your account'}, status=status.HTTP_201_CREATED)


class RegisterStudentView(BaseRegisterView):
    """
    Register students into the system
    """
    serializer_class = StudentRegistrationSerializer


class RegisterLecturerView(BaseRegisterView):
    """
    Register lecturers into the system
    """
    serializer_class = LecturerRegistrationSerializer


class LoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class SendActivationTokenView(APIView):
    """
    Send an account activation token to a user
    """
    def post(self, request, *args, **kwargs):
        serializer = SendActivationTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        email_manager.send_activation_email(user)
        return Response({ 'message': 'Please check your email to verify your account'}, status=status.HTTP_200_OK)


class ActivateAccountView(APIView):
    """
    View to activate user account using UID and token
    """
    @transaction.atomic
    def get(self, request):
        serializer = ActivateAccountSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token = serializer.validated_data['token']
        user.is_active = True
        token.is_used = True
        user.save()
        token.save()
        return Response({ 'message': 'Account activated successfully'}, status=status.HTTP_200_OK)


class ForgottenPasswordView(APIView):
    """
    View to reset a users password if forgotten
    """
    def post(self, request):
        serializer = ForgottenPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = CustomUser.objects.get(email=email)
            email_manager.send_password_reset_email(user)
            return Response({ 'message': f'Password reset instructions sent to {email}'}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({ 'message': 'No user with that email address'}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    """
    View to reset a users password
    """
    def post(self, request, token):
        request.data['token'] = token
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
