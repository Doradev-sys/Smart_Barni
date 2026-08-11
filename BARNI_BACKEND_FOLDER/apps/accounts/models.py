from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('Cashier', 'Cashier'),
        ('Waitstaff', 'Waitstaff'),
        ('Kitchen', 'Kitchen'),
        ('Manager', 'Manager'),
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Cashier')

    def __str__(self):
        return f"{self.username} ({self.role})"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Profile for {self.user.username}"

class LoginAuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} logged in at {self.login_time}"