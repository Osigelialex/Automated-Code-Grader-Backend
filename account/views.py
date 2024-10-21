import base64
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser, Token
from .tokens import account_activation_token
from django.utils import timezone
from django.db import transaction
from .serializers import StudentRegistrationSerializer, LecturerRegistrationSerializer


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

        if account_activation_token.check_token(user, token_key):
            user.is_active = True
            token.is_used = True
            user.save()
            token.save()
            return Response(
                {'message': 'Your account has been confirmed. You can now login'},
                status=status.HTTP_200_OK
            )

        return self.invalid_link_response()

    def invalid_link_response(self):
        return Response(
            {'message': 'Activation link is invalid!'},
            status=status.HTTP_400_BAD_REQUEST
        )
