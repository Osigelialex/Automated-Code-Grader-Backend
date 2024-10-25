from django.urls import path
from .views import CourseCreationView, JoinCourseView


urlpatterns = [
    path('', CourseCreationView.as_view(), name='course-list'),
    path('join/', JoinCourseView.as_view(), name='join-course'),
]
