from django.urls import path
from assignment.views import AssignmentCreateView, AssignmentListView
from .views import (
    JoinCourseView,
    StudentCourseListView,
    UnenrollView,
    CourseListCreateView,
    CourseDetailView
)


urlpatterns = [
    path('courses', CourseListCreateView.as_view(), name='course-list-create'),
    path('courses/join', JoinCourseView.as_view(), name='join-course'),
    path('courses/enrolled', StudentCourseListView.as_view(), name='student-course-list'),
    path('courses/<str:pk>/unenroll', UnenrollView.as_view(), name='unenroll'),
    path('courses/<str:pk>/assignments/create', AssignmentCreateView.as_view(), name='create-assignment'),
    path('courses/<str:pk>/assignments', AssignmentListView.as_view(), name='list-course-assignment'),
    path('courses/<str:pk>', CourseDetailView.as_view(), name='course-detail')
]
