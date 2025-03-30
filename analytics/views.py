from rest_framework.views import APIView
from rest_framework.response import Response
from assignment.models import Submission, Assignment
from account.permissions import IsStudentPermission


class StudentDashboardQuickStatsView(APIView):
    """
    Display's quick statistics for the students dashboard
    """
    permission_classes = [IsStudentPermission]

    def get(self, request, *args, **kwargs):
        submissions = Submission.objects.filter(student=request.user).all()
        total_score = sum(submission.score for submission in submissions)
        total_submissions = submissions.count()
        average_score = 0 if total_submissions == 0 else total_score // total_submissions

        pending_assignments = Assignment.objects.filter(is_draft=False).exclude(
            submissions__student=request.user).count()
        non_optimal_submissions = submissions.filter(is_best=False).count()

        return Response({
            'total_score': total_score,
            'total_submissions': total_submissions,
            'average_score': average_score,
            'pending_assignments': pending_assignments,
            'non_optimal_submissions': non_optimal_submissions
        })


class AssignmentStatusPieChartView(APIView):
    """
    Returns the status of the students assignments to be displayed in a pie chart
    """
    permission_classes = [IsStudentPermission]

    def get(self, request, *args, **kwargs):
        submissions = Submission.objects.filter(student=request.user).all()
        pending_assignments = Assignment.objects.filter(is_draft=False).exclude(
            submissions__student=request.user).count()
        pending = submissions.filter(is_best=False).count()
        completed = submissions.filter(is_best=True).count()

        return Response({
            'pending': pending,
            'completed': completed,
            'pending_assignments': pending_assignments
        })
