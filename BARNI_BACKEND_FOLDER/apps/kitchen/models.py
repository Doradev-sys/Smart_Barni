from django.db import models
from django.conf import settings
from apps.orders.models import Order
import uuid


class KitchenOrder(models.Model):
    STATUS_CHOICES = (
        ('queued', 'Queued'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('done', 'Done'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='kitchen_entry')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='kitchen_orders')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Kitchen: {self.order.order_id} ({self.status})"
