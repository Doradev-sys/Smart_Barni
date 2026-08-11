from rest_framework.permissions import BasePermission

from .models import User


class HasRole(BasePermission):
    """
    Base class — subclass and set `allowed_roles` rather than instantiating
    directly. Keeps every other app's permission checks to one line, e.g.:

        permission_classes = [IsAdminOrKitchenHead]
    """

    allowed_roles = ()

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in self.allowed_roles
        )


class IsAdmin(HasRole):
    allowed_roles = (User.Role.ADMIN,)


class IsSystemAdmin(HasRole):
    allowed_roles = (User.Role.SYSTEM_ADMIN,)


class IsAdminOrSystemAdmin(HasRole):
    allowed_roles = (User.Role.ADMIN, User.Role.SYSTEM_ADMIN)


class IsWaiter(HasRole):
    allowed_roles = (User.Role.WAITER,)


class IsKitchenHead(HasRole):
    allowed_roles = (User.Role.KITCHEN_HEAD,)


class IsKitchenStaff(HasRole):
    allowed_roles = (User.Role.KITCHEN_STAFF,)


class IsAdminOrKitchenHead(HasRole):
    allowed_roles = (User.Role.ADMIN, User.Role.KITCHEN_HEAD)


class IsKitchenHeadOrStaff(HasRole):
    allowed_roles = (User.Role.KITCHEN_HEAD, User.Role.KITCHEN_STAFF)


class IsDeliveryDriver(HasRole):
    allowed_roles = (User.Role.DELIVERY_DRIVER,)


class IsCustomer(HasRole):
    allowed_roles = (User.Role.CUSTOMER,)


class IsOwnerOfObject(BasePermission):
    """Object-level check: user can only view/edit their own record (e.g. profile)."""

    def has_object_permission(self, request, view, obj):
        return getattr(obj, "user_id", None) == request.user.id or obj == request.user
