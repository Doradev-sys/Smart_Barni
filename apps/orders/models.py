from django.db import models
from django.conf import settings
from apps.menu.models import MenuItem



class RestaurantTable(models.Model):

    table_number = models.CharField(
        max_length=10,
        unique=True
    )

    status = models.CharField(
        max_length=20,
        default="available"
    )


    def __str__(self):
        return self.table_number



class Order(models.Model):

    table = models.ForeignKey(
        RestaurantTable,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    waiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    status = models.CharField(
        max_length=20,
        default="received"
    )


    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )


    def __str__(self):
        return f"Order {self.id}"



class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE
    )

    item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )


    def __str__(self):
        return self.item.name