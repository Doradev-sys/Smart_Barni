from rest_framework.permissions import BasePermission

WAITSTAFF_ROLES = {"WAITER", "WAITSTAFF"}


class IsWaitstaff(BasePermission):
    message = "Only branch-assigned waitstaff can perform waiter-interface actions."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role_name", "") in WAITSTAFF_ROLES
            and getattr(user, "branch_id", None) is not None
        )
