from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # ADD THIS INNER CLASS
    class Role:
        ADMIN = 'Admin'
        WAITER = 'Waiter'
        KITCHEN = 'Kitchen'
        CUSTOMER = 'Customer'
        SYSTEM_ADMIN = 'Admin'
        KITCHEN_HEAD = 'Kitchen'
        KITCHEN_STAFF = 'Kitchen'
        DELIVERY_DRIVER = 'Customer'

    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Waiter', 'Waiter'),
        ('Kitchen', 'Kitchen'),
        ('Customer', 'Customer'),
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Waiter')

    def __str__(self):
        return f"{self.username} ({self.role})"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    father_name = models.CharField(max_length=100, blank=True, null=True)  # ADD THIS
    created_at = models.DateTimeField(auto_now_add=True)  # ADD THIS

    def __str__(self):
        return f"Profile for {self.user.username}"

    def __str__(self):
        return f"Profile for {self.user.username}"
class LoginAuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} logged in at {self.login_time}"