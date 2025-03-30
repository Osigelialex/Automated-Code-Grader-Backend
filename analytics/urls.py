from django.urls import path
from .views import StudentDashboardQuickStatsView, AssignmentStatusPieChartView

urlpatterns = [
    path('analytics/student-dashboard-quick-stats', StudentDashboardQuickStatsView.as_view(), name='student-dashboard-quick-stats'),
    path('analytics/student-assignment-status', AssignmentStatusPieChartView.as_view(), name='assignment-status-pie-chart'),
]