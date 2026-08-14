from django.db import models


class Branch(models.Model):
    branch_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "branches"
        ordering = ["name"]

    def __str__(self):
        return self.name


class DiningTable(models.Model):
    class Status(models.TextChoices):
        FREE = "FREE", "Free"
        OCCUPIED = "OCCUPIED", "Occupied"
        RESERVED = "RESERVED", "Reserved"
        CLEANING = "CLEANING", "Cleaning"

    table_id = models.BigAutoField(primary_key=True)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="dining_tables", db_column="branch_id")
    table_number = models.CharField(max_length=20)
    capacity = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.FREE)
    location = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = "dining_tables"
        ordering = ["branch_id", "table_number"]
        constraints = [
            models.UniqueConstraint(fields=["branch", "table_number"], name="uq_dining_table_branch_number")
        ]

    def __str__(self):
        return f"{self.table_number} - {self.branch.name}"
