from rest_framework.permissions import BasePermission


class HasRole(BasePermission):
    """
    Base permission class.
    Checks if the logged-in user has an allowed role.
    """

    allowed_roles = []


    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        return request.user.role in self.allowed_roles



class AdminOnly(HasRole):
    """
    Only Admin users
    """

    allowed_roles = [
        "admin"
    ]



class ManagerOnly(HasRole):
    """
    Only Manager users
    """

    allowed_roles = [
        "manager"
    ]



class AdminManagerOnly(HasRole):
    """
    Admin and Manager users
    """

    allowed_roles = [
        "admin",
        "manager"
    ]



class CashierOnly(HasRole):
    """
    Only Cashier users
    """

    allowed_roles = [
        "cashier"
    ]



class WaiterOnly(HasRole):
    """
    Only Waiter users
    """

    allowed_roles = [
        "waiter"
    ]



class ChefOnly(HasRole):
    """
    Only Chef users
    """

    allowed_roles = [
        "chef"
    ]



class DeliveryOnly(HasRole):
    """
    Only Delivery users
    """

    allowed_roles = [
        "delivery"
    ]



class StaffOnly(HasRole):
    """
    All staff users except unauthenticated users
    """

    allowed_roles = [
        "admin",
        "manager",
        "cashier",
        "waiter",
        "chef",
        "delivery",
    ]