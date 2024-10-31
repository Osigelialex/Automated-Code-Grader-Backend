from django.urls import path, include
from .views import AssignmentDetailView, AssignmentSubmissionView

urlpatterns = [
    path('<int:pk>/', AssignmentDetailView.as_view(), name='assignment-detail'),
    path('<int:pk>/submit/', AssignmentSubmissionView.as_view(), name='assignment-submit'),
]
