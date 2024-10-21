from django.urls import path
from .views import RegisterLecturerView, RegisterStudentView, ActivateAccountView


urlpatterns = [
    path('register/student/', RegisterStudentView.as_view(), name='student-register'),
    path('register/lecturer/', RegisterLecturerView.as_view(), name='lecturer-register'),
    path('activate/', ActivateAccountView.as_view(), name='activate-account')
]