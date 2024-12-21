from django.urls import path
from .views import (
    RegisterLecturerView,
    RegisterStudentView,
    ActivateAccountView,
    ForgottenPasswordView,
    LoginView,
    SendActivationTokenView,
    ResetPasswordView,
    RefreshTokenView,
    LogoutView,
    FetchProfileView
)


urlpatterns = [
    path('register-student', RegisterStudentView.as_view(), name='student-register'),
    path('register-lecturer', RegisterLecturerView.as_view(), name='lecturer-register'),
    path('activate', ActivateAccountView.as_view(), name='activate-account'),
    path('login', LoginView.as_view(), name='login'),
    path('refresh', RefreshTokenView.as_view(), name='token_refresh'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('request-password-reset', ForgottenPasswordView.as_view(), name='reset-password'),
    path('<str:token>/reset-password', ResetPasswordView.as_view(), name='reset-password'),
    path('send-activation-token', SendActivationTokenView.as_view(), name='send-activation-token'),
    path('profile', FetchProfileView.as_view(), name='profile'),
]