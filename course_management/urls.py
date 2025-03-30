from django.urls import path
from assignment.views import AssignmentCreateView, AssignmentListView
from .views import (
    JoinCourseView,
    StudentCourseListView,
    UnenrollView,
    CourseListCreateView,
    CourseDetailView,
    CourseEditView,
    CourseDeleteView
)


urlpatterns = [
    path('courses', CourseListCreateView.as_view(), name='course-list-create'),
    path('courses/join', JoinCourseView.as_view(), name='join-course'),
    path('courses/enrolled', StudentCourseListView.as_view(), name='student-course-list'),
    path('courses/<uuid:pk>/unenroll', UnenrollView.as_view(), name='unenroll'),
    path('courses/<uuid:pk>/assignments/create', AssignmentCreateView.as_view(), name='create-assignment'),
    path('courses/<uuid:pk>/assignments', AssignmentListView.as_view(), name='list-course-assignment'),
    path('courses/<uuid:pk>', CourseDetailView.as_view(), name='course-detail'),
    path('courses/<uuid:pk>/edit', CourseEditView.as_view(), name='course-edit'),
    path('courses/<uuid:pk>/delete', CourseDeleteView.as_view(), name='course-delete')
]
