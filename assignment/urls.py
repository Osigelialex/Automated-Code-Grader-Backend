from django.urls import path
from .views import (
    AssignmentDetailView,
    AssignmentSubmissionView,
    StudentSubmissionListView,
    SubmissionDetailView,
    AssignmentResultData,
    FeedbackGenerationView,
    RateFeedbackView,
    FeedbackListView,
    PublishAssignmentView
    )

urlpatterns = [
    path('assignments/<str:pk>', AssignmentDetailView.as_view(), name='assignment-detail'),
    path('assignments/<str:pk>/submit', AssignmentSubmissionView.as_view(), name='assignment-submit'),
    path('assignments/<str:pk>/submissions', StudentSubmissionListView.as_view(), name='student-submissions'),
    path('assignments/<str:pk>/publish', PublishAssignmentView.as_view(), name='publish-assignment'),
    path('submissions/<str:pk>', SubmissionDetailView.as_view(), name='submission-detail'),
    path('assignments/<str:pk>/results', AssignmentResultData.as_view(), name='assignment-result'),
    path('submissions/<str:submission_id>/feedback', FeedbackGenerationView.as_view(), name='generate-feedback'),
    path('feedback/<str:feedback_id>/rate', RateFeedbackView.as_view(), name='rate-feedback'),
    path('feedback', FeedbackListView.as_view(), name='feedback-list')
]
