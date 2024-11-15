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
    path('assignment/<str:pk>/', AssignmentDetailView.as_view(), name='assignment-detail'),
    path('assignment/<str:pk>/submit/', AssignmentSubmissionView.as_view(), name='assignment-submit'),
    path('assignment/<str:pk>/submissions/', StudentSubmissionListView.as_view(), name='student-submissions'),
    path('submission/<str:pk>/', SubmissionDetailView.as_view(), name='submission-detail'),
    path('assignment/<str:pk>/results/', AssignmentResultData.as_view(), name='assignment-result'),
    path('submission/<str:submission_id>/feedback/', FeedbackGenerationView.as_view(), name='generate-feedback'),
    path('feedback/<str:feedback_id>/rate/', RateFeedbackView.as_view(), name='rate-feedback'),
    path('feedback/', FeedbackListView.as_view(), name='feedback-list')
]
