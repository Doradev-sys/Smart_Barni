from django.db import models
from django.conf import settings
from apps.menu.models import MenuItem



class Supplier(models.Model):

    name = models.CharField(
        max_length=100
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    address = models.TextField(
        blank=True
    )


    def __str__(self):
        return self.name



class Ingredient(models.Model):

    name = models.CharField(
        max_length=100
    )

    unit = models.CharField(
        max_length=20,
        help_text="kg, liter, piece"
    )

    quantity_available = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    minimum_stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )


    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )


    def __str__(self):
        return self.name



class Recipe(models.Model):

    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name="recipe"
    )


    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )


    quantity_required = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )


    def __str__(self):
        return f"{self.menu_item} - {self.ingredient}"