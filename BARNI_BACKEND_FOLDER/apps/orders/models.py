from django.core.validators import MinValueValidator
from django.db import models

class Order(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        SENT = "SENT", "Sent"
        IN_PREP = "IN_PREP", "In preparation"
        READY = "READY", "Ready"
        SERVED = "SERVED", "Served"
        CLOSED = "CLOSED", "Closed"
        CANCELLED = "CANCELLED", "Cancelled"

    class OrderType(models.TextChoices):
        DINE_IN = "DINE_IN", "Dine in"
        DELIVERY = "DELIVERY", "Delivery"
        TAKEAWAY = "TAKEAWAY", "Takeaway"

    order_id = models.BigAutoField(primary_key=True)
    branch = models.ForeignKey("branches.Branch", on_delete=models.PROTECT, related_name="orders", db_column="branch_id")
    table = models.ForeignKey("branches.DiningTable", on_delete=models.PROTECT, related_name="orders", db_column="table_id", blank=True, null=True)
    waiter = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="waiter_orders", db_column="waiter_id", blank=True, null=True)
    customer = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="customer_orders", db_column="customer_id", blank=True, null=True)
    order_timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.OPEN)
    order_type = models.CharField(max_length=20, choices=OrderType.choices)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    payment_method = models.CharField(max_length=30, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "orders"
        ordering = ["-order_timestamp"]
        indexes = [
            models.Index(fields=["branch", "-order_timestamp"], name="orders_branch_ts_idx"),
            models.Index(fields=["waiter", "-order_timestamp"], name="orders_waiter_ts_idx"),
        ]

    def __str__(self):
        return f"#{self.order_id} {self.order_type} {self.status}"


class OrderItem(models.Model):
    class PrepStatus(models.TextChoices):
        QUEUED = "QUEUED", "Queued"
        IN_PREP = "IN_PREP", "In preparation"
        READY = "READY", "Ready"
        SERVED = "SERVED", "Served"
        VOID = "VOID", "Void"

    order_item_id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="items", db_column="order_id")
    item = models.ForeignKey("menu.MenuItem", on_delete=models.PROTECT, related_name="order_items", db_column="item_id")
    quantity = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0.01)])
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    line_total = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    prep_status = models.CharField(max_length=20, choices=PrepStatus.choices, default=PrepStatus.QUEUED)
    kitchen_station = models.CharField(max_length=40, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    sent_to_kitchen_at = models.DateTimeField(blank=True, null=True)
    ready_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "order_items"
        ordering = ["order_item_id"]
        indexes = [models.Index(fields=["prep_status"], name="order_items_prep_idx")]

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"
