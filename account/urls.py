from django.urls import path
from .views import (
    RegisterLecturerView,
    RegisterStudentView,
    ActivateAccountView,
    ForgottenPasswordView,
    LoginView,
    SendActivationTokenView,
    ResetPasswordView,
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenBlacklistView
)


urlpatterns = [
    path('register/student/', RegisterStudentView.as_view(), name='student-register'),
    path('register/lecturer/', RegisterLecturerView.as_view(), name='lecturer-register'),
    path('activate/', ActivateAccountView.as_view(), name='activate-account'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', TokenBlacklistView.as_view(), name='logout'),
    path('request_password_reset/', ForgottenPasswordView.as_view(), name='reset-password'),
    path('reset_password/<str:token>/', ResetPasswordView.as_view(), name='reset-password'),
    path('send-activation-token/', SendActivationTokenView.as_view(), name='send-activation-token'),
]