from django.urls import path, include
from .views import AssignmentDetailView
from .views import AssignmentSubmitAPIView

urlpatterns = [
    path('<int:pk>/', AssignmentDetailView.as_view(), name='assignment-detail'),
    path('<int:pk>/submit/', AssignmentSubmitAPIView.as_view(), name='assignment-submit'),
]
