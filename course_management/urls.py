from django.urls import path
from assignment.views import AssignmentCreateView, StudentAssignmentListView
from .views import (
    JoinCourseView,
    StudentCourseListView,
    UnenrollView,
    CourseListCreateView
)


urlpatterns = [
    path('', CourseListCreateView.as_view(), name='course-list-create'),
    path('join/', JoinCourseView.as_view(), name='join-course'),
    path('enrolled/', StudentCourseListView.as_view(), name='student-course-list'),
    path('<str:course_id>/unenroll/', UnenrollView.as_view(), name='unenroll'),
    path('<str:course_id>/create-assignment/', AssignmentCreateView.as_view(), name='create-assignment'),
    path('<str:course_id>/list-assignments/', StudentAssignmentListView.as_view(), name='list-course-assignment'),
]
