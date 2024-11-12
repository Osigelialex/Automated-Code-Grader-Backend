from django.urls import path
from .views import (
    AssignmentDetailView,
    AssignmentSubmissionView,
    StudentSubmissionListView,
    SubmissionDetailView,
    AssignmentResultData,
    FeedbackGenerationView,
    RateFeedbackView,
    FeedbackListView
    )

urlpatterns = [
    path('assignment/<int:pk>/', AssignmentDetailView.as_view(), name='assignment-detail'),
    path('assignment/<int:pk>/submit/', AssignmentSubmissionView.as_view(), name='assignment-submit'),
    path('assignment/<int:pk>/submissions/', StudentSubmissionListView.as_view(), name='student-submissions'),
    path('submission/<int:pk>/', SubmissionDetailView.as_view(), name='submission-detail'),
    path('assignment/<int:pk>/results/', AssignmentResultData.as_view(), name='assignment-result'),
    path('submission/<int:submission_id>/feedback/', FeedbackGenerationView.as_view(), name='generate-feedback'),
    path('feedback/<int:feedback_id>/rate/', RateFeedbackView.as_view(), name='rate-feedback'),
    path('feedback/', FeedbackListView.as_view(), name='feedback-list')
]
