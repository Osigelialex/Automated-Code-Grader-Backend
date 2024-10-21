from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'student'


class IsLecturer(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'lecturer'
