from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser
from django.db import transaction
from .tasks import send_activation_email, send_password_reset_email
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken
from course_management.serializers import MessageSerializer
from .email_manager import email_manager
from .serializers import (
    StudentRegistrationSerializer,
    LecturerRegistrationSerializer,
    ForgottenPasswordSerializer,
    LoginUserSerializer,
    ResetPasswordSerializer,
    ActivateAccountSerializer,
    ProfileDetailSerializer
)


class BaseRegisterationView(APIView):
    """
    Base view for registering a student
    """
    authentication_classes = []

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        try:
            email_manager.send_activation_email(user.id, user.first_name, user.email)
        except Exception as e:
            return Response({'message': 'Could not send your activation email'}, status=400)
        
        # store users email in httpOnly cookie for email resending purposes
        response = Response({'message': 'Please check your email to verify your account'}, status=status.HTTP_201_CREATED)
        response.set_cookie(key='email', value=user.email, httponly=True, secure=True, samesite='None', domain='checkmater.vercel.app')
        return response


@extend_schema(
    responses={
        201: MessageSerializer
    }
)
class RegisterStudentView(BaseRegisterationView):
    """
    Register students into the system
    """
    serializer_class = StudentRegistrationSerializer


@extend_schema(
    responses={
        201: MessageSerializer
    }
)
class RegisterLecturerView(BaseRegisterationView):
    """
    Register lecturers into the system
    """
    serializer_class = LecturerRegistrationSerializer


class LoginView(TokenObtainPairView):
    serializer_class = LoginUserSerializer
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({'message': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data
        if not user.email_verified:
            try:
                email_manager.send_activation_email(user.id, user.first_name, user.email)
            except Exception as e:
                return Response({'message': 'Could not send your activation email'}, status=400)

            return Response({'message': 'Account not activated'}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        refresh['role'] = user.role

        response = Response({ 'message': 'Login successful', 'role': user.role}, status=status.HTTP_200_OK)
        response.set_cookie(key='access_token', value=str(access), httponly=True, secure=True, samesite='None', domain='checkmater.vercel.app')
        response.set_cookie(key='refresh_token', value=str(refresh), httponly=True, secure=True, samesite='None', domain='checkmater.vercel.app')
        return response


class SendActivationTokenView(APIView):
    """
    Send an account activation token to a user
    """
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        # retrieve users email from httpOnly cookie
        email = request.COOKIES.get('email')

        try:
            user = CustomUser.objects.get(email=email)

            # verify that the user's account is not activated
            if user.email_verified == True:
                return Response({ 'message': 'Account already activated'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                email_manager.send_activation_email(user.id, user.first_name, user.email)
            except Exception as e:
                return Response({'message': 'Could not send your activation email'}, status=400)
            
            return Response({ 'message': 'Please check your email to verify your account'}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({ 'message': 'No user with that email address' }, status=status.HTTP_404_NOT_FOUND)


class RefreshTokenView(APIView):
    """
    Refreshes the access token using the refresh token
    """
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'message': 'Refresh token not included'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            response = Response({'message': 'Token refreshed successfully'}, status=status.HTTP_200_OK)
            response.set_cookie(key='access_token', value=access_token, httponly=True, secure=True, samesite='None', domain='checkmater.vercel.app')

            return response
        except InvalidToken:
            return Response({ 'message': 'Refresh token is invalid'}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    Logs out a user by blacklisting their refresh token and deleting the access and refresh tokens from cookies
    """
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response({'message': 'Already logged out'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            refresh.blacklist()
        
            response = Response({'message': 'Successfully logged out'})
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')

            return response

        except Exception as e:
            return Response({ 'message': 'Could not invalidate token'}, status=status.HTTP_400_BAD_REQUEST)


class ActivateAccountView(APIView):
    """
    View to activate user account using UID and token
    """
    serializer_class = ActivateAccountSerializer
    authentication_classes = []

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="token",
                description="Account activation token",
                type=str
            )
        ],
        responses={
            200: MessageSerializer,
            400: MessageSerializer
        }
    )
    @transaction.atomic
    def patch(self, request):
        serializer = self.serializer_class(data=request.query_params)
        if not serializer.is_valid():
            return Response({ 'message': 'Link is invalid or expired' }, status=status.HTTP_404_NOT_FOUND)

        user = serializer.validated_data['user']
        if user.email_verified:
            return Response({ 'message': 'Account already activated'}, status=status.HTTP_400_BAD_REQUEST)

        user.email_verified = True
        user.save()

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        refresh['role'] = user.role

        response = Response({ 'message': 'Account activated successfully'}, status=status.HTTP_200_OK)
        response.set_cookie(key='access_token', value=str(access_token), httponly=True, secure=True, samesite='None', domain='checkmater.vercel.app')
        response.set_cookie(key='refresh_token', value=str(refresh), httponly=True, secure=True, samesite='None', domain='checkmater.vercel.app')
        return response


class ForgottenPasswordView(APIView):
    """
    View to reset a users password if forgotten
    """
    serializer_class = ForgottenPasswordSerializer
    authentication_classes = []

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = CustomUser.objects.get(email=email)
            try:
                email_manager.send_password_reset_email(user.id, user.first_name, user.email)
            except Exception as e:
                return Response({'message': 'Could not send your password reset email'}, status=400)
            return Response({ 'message': f'Password reset instructions sent to {email}'}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({ 'message': 'No user with that email address'}, status=status.HTTP_404_NOT_FOUND)


class ResetPasswordView(APIView):
    """
    View to reset a users password
    """
    serializer_class = ResetPasswordSerializer
    authentication_classes = []

    @extend_schema(
        responses={
            200: MessageSerializer
        }
    )
    @transaction.atomic
    def post(self, request, token):
        request.data['token'] = token
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)


class FetchProfileView(generics.RetrieveAPIView):
    """
    Fetches the profile of the currently logged in user
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileDetailSerializer

    def get_object(self):
        return self.request.user