from django.urls import path, include
from .views import (
    AssignmentDetailView,
    AssignmentSubmissionView,
    StudentSubmissionListView,
    SubmissionDetailView)

urlpatterns = [
    path('<int:pk>/', AssignmentDetailView.as_view(), name='assignment-detail'),
    path('<int:pk>/submit/', AssignmentSubmissionView.as_view(), name='assignment-submit'),
    path('<int:pk>/submissions/', StudentSubmissionListView.as_view(), name='student-submissions'),
    path('submissions/<int:pk>/', SubmissionDetailView.as_view(), name='submission-detail'),
]
