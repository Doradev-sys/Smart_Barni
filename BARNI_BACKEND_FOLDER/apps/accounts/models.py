from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models


class User(AbstractUser):
    class Role:
        ADMIN = 'Admin'
        WAITER = 'Waiter'
        KITCHEN = 'Kitchen'
        CUSTOMER = 'Customer'
        # Compatibility names used elsewhere in the current backend.
        SYSTEM_ADMIN = 'Admin'
        KITCHEN_HEAD = 'Kitchen'
        KITCHEN_STAFF = 'Kitchen'
        DELIVERY_DRIVER = 'DeliveryDriver'

    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Waiter', 'Waiter'),
        ('Kitchen', 'Kitchen'),
        ('Customer', 'Customer'),
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default=Role.WAITER)

    def __str__(self):
        return f"{self.username} ({self.role})"


class CustomerAddress(models.Model):
    """Delivery address owned by exactly one authenticated customer."""
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='delivery_addresses',
    )
    label = models.CharField(max_length=100, blank=True, default='')
    recipient_name = models.CharField(max_length=150, blank=True, default='')
    phone = models.CharField(max_length=20, blank=True, default='')
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=100, blank=True, default='')
    area = models.CharField(max_length=100, blank=True, default='')
    landmark = models.CharField(max_length=255, blank=True, default='')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', '-updated_at']

    def __str__(self):
        return f"{self.customer.username} - {self.label or self.address_line}"


# Existing models are intentionally retained for migration compatibility,
# but Customer Phase 1 does not read from or write to them.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"Profile for {self.user.username}"


class LoginAuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} logged in at {self.login_time}"
