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
    PublishAssignmentView,
    RetrieveProgrammingLanguages,
    RetrieveProgressView,
    TestRunFeedbackGenerationView,
    TeacherAssignmentsList
    )

urlpatterns = [
    path('assignments/<uuid:pk>', AssignmentDetailView.as_view(), name='assignment-detail'),
    path('assignments/<uuid:pk>/submit', AssignmentSubmissionView.as_view(), name='assignment-submit'),
    path('assignments/<uuid:pk>/submissions', StudentSubmissionListView.as_view(), name='student-submissions'),
    path('assignments/<uuid:pk>/publish', PublishAssignmentView.as_view(), name='publish-assignment'),
    path('submissions/<uuid:pk>', SubmissionDetailView.as_view(), name='submission-detail'),
    path('assignments/<uuid:pk>/results', AssignmentResultData.as_view(), name='assignment-result'),
    path('submissions/<uuid:pk>/feedback', FeedbackGenerationView.as_view(), name='generate-feedback'),
    path('feedback/<uuid:pk>/rate', RateFeedbackView.as_view(), name='rate-feedback'),
    path('feedback', FeedbackListView.as_view(), name='feedback-list'),
    path('languages', RetrieveProgrammingLanguages.as_view(), name='programming-languages'),
    path('assignments/<uuid:pk>/progress', RetrieveProgressView.as_view(), name='fetch-progress'),
    path('feedback/test-run', TestRunFeedbackGenerationView.as_view(), name='test-run-feedback'),
    path('assignments/teacher', TeacherAssignmentsList.as_view(), name='teacher-assignments-list')
]
