from django.db import models
from apps.orders.models import Order



class Payment(models.Model):

    PAYMENT_METHODS = (
        ("cash","Cash"),
        ("card","Card"),
        ("telebirr","Telebirr"),
        ("bank","Bank"),
    )


    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE
    )


    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )


    method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS
    )


    status = models.CharField(
        max_length=20,
        default="completed"
    )


    paid_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return f"Payment {self.id}"