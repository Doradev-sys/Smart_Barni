from django.db import models
from django.conf import settings
from apps.orders.models import Order
import uuid


class Payment(models.Model):
    METHOD_CHOICES = (
        ('Chapa', 'Chapa'),
        ('CBE', 'CBE'),
        ('BOA', 'BOA'),
        ('Telebirr', 'Telebirr'),
        ('Awash', 'Awash'),
        ('Cash', 'Cash'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('pending_verification', 'Pending Verification'),  # NEW
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, related_name='payments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reference = models.CharField(max_length=200, blank=True, default='')
    qr_data = models.TextField(blank=True, default='')
    account_number = models.CharField(max_length=50, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    phone = models.CharField(max_length=20, blank=True, default='')
    
    # NEW FIELDS
    proof_image = models.ImageField(upload_to='payment_proofs/', blank=True, null=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='verified_payments'
    )
    verified_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.id} - {self.method} - {self.amount}"