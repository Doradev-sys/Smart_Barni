from django.db import models


class Category(models.Model):

    name = models.CharField(
        max_length=100
    )

    meal_period = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )


    def __str__(self):
        return self.name



class MenuItem(models.Model):

    name = models.CharField(
        max_length=100
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="items"
    )

    description = models.TextField(
        blank=True
    )

    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    active = models.BooleanField(
        default=True
    )


    def __str__(self):
        return self.name