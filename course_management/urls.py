from django.urls import path
from .views import (
    CourseCreationView,
    JoinCourseView,
    StudentCourseListView,
    LecturerCourseListView
)


urlpatterns = [
    path('', CourseCreationView.as_view(), name='course-list'),
    path('join/', JoinCourseView.as_view(), name='join-course'),
    path('enrolled/', StudentCourseListView.as_view(), name='student-course-list'),
    path('teaching/', LecturerCourseListView.as_view(), name='lecturer-course-list'),
]
