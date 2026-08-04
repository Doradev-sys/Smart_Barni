from django.db import models
from django.conf import settings
from apps.inventory.models import Ingredient



class Alert(models.Model):

    ALERT_TYPES = (
        ("stock","Low Stock"),
        ("system","System"),
        ("payment","Payment"),
    )


    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPES
    )


    message = models.TextField()


    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )


    created_for = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )


    is_read = models.BooleanField(
        default=False
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return self.message