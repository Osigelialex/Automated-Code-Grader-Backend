import base64
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser, Token
from django.utils import timezone
from django.db import transaction
from .email_manager import email_manager
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    StudentRegistrationSerializer,
    LecturerRegistrationSerializer,
    ForgottenPasswordSerializer,
    MyTokenObtainPairSerializer,
    SendActivationTokenSerializer)


class RegisterStudentView(generics.CreateAPIView):
    """
    Register students into the system
    """
    serializer_class = StudentRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Please check your email to verify your account'}, status=status.HTTP_201_CREATED)


class RegisterLecturerView(generics.CreateAPIView):
    """
    Register lecturers into the system
    """
    serializer_class = LecturerRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Please check your email to verify your account'}, status=status.HTTP_201_CREATED)


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
    View to activate user account
    """
    @transaction.atomic
    def get(self, request):
        uid = request.GET.get('uid')
        token_key = request.query_params.get('token')
        if not uid or not token_key:
            return self.invalid_link_response()

        try:
            user_id = base64.b64decode(uid).decode('utf-8')
            user = CustomUser.objects.get(pk=user_id)
            token = Token.objects.get(key=token_key)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist, Token.DoesNotExist):
            return self.invalid_link_response()

        if token.is_used or token.expires_at < timezone.now():
            return self.invalid_link_response()

        # update the users account status
        user.is_active = True
        token.is_used = True
        user.save()
        token.save()

        return Response({'message': 'Your account has been confirmed. You can now login'},status=status.HTTP_200_OK)

    def invalid_link_response(self):
        return Response(
            {'message': 'Activation link is invalid!'},
            status=status.HTTP_400_BAD_REQUEST
        )


class ForgottenPasswordView(APIView):
    """
    View to reset a users password if forgotten
    """
    def post(self, request):
        serialzer = ForgottenPasswordSerializer(data=request.data)
        serialzer.is_valid(raise_exception=True)
        user = CustomUser.objects.filter(email=request.data)
        email_manager.send_password_reset_email(user)
        return Response({ 'message': f"An email to reset your password has been sent to {request.data}"},
                        status=status.HTTP_200_OK)
