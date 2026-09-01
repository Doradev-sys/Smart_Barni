from rest_framework.permissions import BasePermission
from .models import User


class HasRole(BasePermission):
    allowed_roles = ()

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in self.allowed_roles
        )


class IsAdmin(HasRole):
    allowed_roles = (User.Role.ADMIN,)


class IsSystemAdmin(IsAdmin):
    pass


class IsAdminOrSystemAdmin(IsAdmin):
    pass


class IsWaiter(HasRole):
    allowed_roles = (User.Role.WAITER,)


class IsKitchenHead(HasRole):
    allowed_roles = (User.Role.KITCHEN,)


class IsKitchenStaff(IsKitchenHead):
    pass


class IsAdminOrKitchenHead(HasRole):
    allowed_roles = (User.Role.ADMIN, User.Role.KITCHEN)


class IsKitchenHeadOrStaff(IsKitchenHead):
    pass


class IsDeliveryDriver(HasRole):
    allowed_roles = (User.Role.DELIVERY_DRIVER,)


class IsCustomer(HasRole):
    allowed_roles = (User.Role.CUSTOMER,)


class IsOwnerOfObject(BasePermission):
    def has_object_permission(self, request, view, obj):
        return getattr(obj, 'user_id', None) == request.user.id or getattr(obj, 'customer_id', None) == request.user.id or obj == request.user
