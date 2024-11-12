from django.urls import path
from .views import (
    AssignmentDetailView,
    AssignmentSubmissionView,
    StudentSubmissionListView,
    SubmissionDetailView,
    AssignmentResultData,
    FeedbackGenerationView,
    RateFeedbackView
    )

urlpatterns = [
    path('<int:pk>/', AssignmentDetailView.as_view(), name='assignment-detail'),
    path('<int:pk>/submit/', AssignmentSubmissionView.as_view(), name='assignment-submit'),
    path('<int:pk>/submissions/', StudentSubmissionListView.as_view(), name='student-submissions'),
    path('submissions/<int:pk>/', SubmissionDetailView.as_view(), name='submission-detail'),
    path('<int:pk>/result/', AssignmentResultData.as_view(), name='assignment-result'),
    path('feedback/<int:submission_id>/', FeedbackGenerationView.as_view(), name='generate-feedback'),
    path('feedback/<int:feedback_id>/rate/', RateFeedbackView.as_view(), name='rate-feedback')
]
