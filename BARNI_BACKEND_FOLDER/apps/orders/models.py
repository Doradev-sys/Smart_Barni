from django.db import models
from django.conf import settings
from apps.menu.models import MenuItem
import uuid


class Table(models.Model):
    number = models.IntegerField(unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Table {self.number}"


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('served', 'Served'),
        ('declined', 'Declined'),
        ('cancelled', 'Cancelled'),
    )
    SOURCE_CHOICES = (
        ('barni', 'At Barni'),
        ('online', 'Online'),
        ('customer', 'Customer'),
    )
    PAYMENT_CHOICES = (
        ('Chapa', 'Chapa'),
        ('CBE', 'CBE'),
        ('BOA', 'BOA'),
        ('Telebirr', 'Telebirr'),
        ('Awash', 'Awash'),
        ('Cash', 'Cash'),
        ('Online', 'Online'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_id = models.CharField(max_length=20, unique=True)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_orders')
    waiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='waiter_orders')
    side = models.CharField(max_length=50, blank=True, default='Plain')
    quantity = models.PositiveIntegerField(default=1)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default='barni')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, blank=True, default='')
    qr_data = models.TextField(blank=True, default='')
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_id} - {self.menu_item.name if self.menu_item else 'N/A'}"


class Receipt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    receipt_number = models.CharField(max_length=30, unique=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    waiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    table_label = models.CharField(max_length=50, blank=True, default='')
    item_label = models.CharField(max_length=200, blank=True, default='')
    quantity = models.PositiveIntegerField(default=1)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, blank=True, default='')
    qr_data = models.TextField(blank=True, default='')
    printed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Receipt {self.receipt_number}"
