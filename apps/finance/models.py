from django.db import models
from django.conf import settings



class Expense(models.Model):

    CATEGORY = (
        ("food", "Food"),
        ("salary", "Salary"),
        ("utility", "Utility"),
        ("other", "Other"),
    )


    title = models.CharField(
        max_length=100
    )


    category = models.CharField(
        max_length=20,
        choices=CATEGORY
    )


    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
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
        return self.title





class Income(models.Model):

    source = models.CharField(
        max_length=100
    )


    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return self.source