from django.db import models
from django.conf import settings
import uuid

class Alert(models.Model):
    TYPE_CHOICES = (
        ('issue', 'Issue'),
        ('low_stock', 'Low Stock'),
        ('system', 'System'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('responded', 'Responded'),
        ('resolved', 'Resolved'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='authored_alerts')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_alerts')
    alert_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='issue')
    title = models.CharField(max_length=255)
    detail = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    response = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
