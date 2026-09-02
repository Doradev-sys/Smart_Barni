# apps/orders/models.py
# ============================================================================
# COMPLETE ORDERS MODELS FILE
# ============================================================================

from django.db import models
from django.conf import settings
from apps.menu.models import MenuItem
import uuid


class Table(models.Model):
    """Table model for dine-in orders"""
    number = models.IntegerField(unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Table {self.number}"


class OrderItem(models.Model):
    """Individual item within an order"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.menu_item.name} x{self.quantity}"


class Order(models.Model):
    """Order model for customer orders"""
    
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
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    # Primary Key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_id = models.CharField(max_length=20, unique=True)
    
    # Order Details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Order Type
    order_type = models.CharField(
        max_length=20,
        choices=[('dine_in', 'Dine In'), ('delivery', 'Delivery')],
        default='dine_in'
    )
    delivery_address = models.TextField(blank=True, default='')
    estimated_delivery_time = models.DateTimeField(blank=True, null=True)
    
    # Foreign Keys
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customer_orders'
    )
    waiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='waiter_orders'
    )
    
    # Order Details
    side = models.CharField(max_length=50, blank=True, default='Plain')
    quantity = models.PositiveIntegerField(default=1)
    
    # Status Fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default='barni')
    
    # Payment Fields
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, blank=True, default='')
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    
    # Additional Fields
    qr_data = models.TextField(blank=True, default='')
    notes = models.TextField(blank=True, default='')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_id} - ${self.total}"


class Receipt(models.Model):
    """Receipt model for paid orders"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    receipt_number = models.CharField(max_length=30, unique=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    waiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
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