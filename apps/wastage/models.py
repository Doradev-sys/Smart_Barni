from django.db import models
from django.conf import settings
from apps.inventory.models import Ingredient



class Wastage(models.Model):


    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )


    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )


    reason = models.CharField(
        max_length=200
    )


    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return self.ingredient.name