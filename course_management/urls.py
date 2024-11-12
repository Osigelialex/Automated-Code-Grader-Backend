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
    path('<int:course_id>/unenroll/', UnenrollView.as_view(), name='unenroll'),
    path('<int:course_id>/create-assignment/', AssignmentCreateView.as_view(), name='create-assignment'),
    path('<int:course_id>/list-assignments/', StudentAssignmentListView.as_view(), name='list-course-assignment'),
]
