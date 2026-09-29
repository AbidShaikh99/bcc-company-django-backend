from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    message = "Only admin users can perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if not request.user.role:
            return False

        return request.user.role.role_code == "ADMIN"

from rest_framework.permissions import BasePermission


class CanManageUsers(BasePermission):

    message = "Only admin or manager users can create users."

    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:
            return False

        role = request.user.role

        if not role:
            return False

        # ADMIN can create users
        if role.role_code == "ADMIN":
            return True

        # Any manager with permission can create users
        if role.can_create_users:
            return True

        return False