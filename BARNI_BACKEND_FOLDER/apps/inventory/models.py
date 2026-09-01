from django.db import models
from django.conf import settings
import uuid


class InventoryItem(models.Model):
    CATEGORY_CHOICES = (
        ('raw', 'Raw Ingredient'),
        ('processed', 'Processed'),
        ('packaging', 'Packaging'),
        ('cleaning', 'Cleaning'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='raw')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit = models.CharField(max_length=20, default='kg')
    min_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Low-stock alert threshold')
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"

    @property
    def is_low_stock(self):
        return self.quantity <= self.min_threshold
