from rest_framework.permissions import BasePermission


class IsStudentPermission(BasePermission):
    """
    Permission class to only allow students to access a view
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'STUDENT'


class IsLecturerPermission(BasePermission):
    """
    Permission class to only allow lecturers to access a view
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'LECTURER'
