from django.db import models

class Alert(models.Model):
    class AlertType(models.TextChoices):
        LOW_STOCK = "LOW_STOCK", "Low stock"
        MISSING_INGREDIENT = "MISSING_INGREDIENT", "Missing ingredient"
        WASTAGE = "WASTAGE", "Wastage"
        UNPROFITABLE = "UNPROFITABLE", "Unprofitable"
        VARIANCE = "VARIANCE", "Variance"

    class Severity(models.TextChoices):
        INFO = "INFO", "Info"
        WARNING = "WARNING", "Warning"
        CRITICAL = "CRITICAL", "Critical"
    class AckStatus(models.TextChoices):
        OPEN = "OPEN", "Open"
        ACKNOWLEDGED = "ACKNOWLEDGED", "Acknowledged"
        RESOLVED = "RESOLVED", "Resolved"

    alert_id = models.BigAutoField(primary_key=True)
    alert_type = models.CharField(max_length=40, choices=AlertType.choices)
    ingredient = models.ForeignKey("inventory.Ingredient", on_delete=models.PROTECT, related_name="alerts", db_column="ingredient_id", blank=True, null=True)
    item = models.ForeignKey("menu.MenuItem", on_delete=models.PROTECT, related_name="alerts", db_column="item_id", blank=True, null=True)
    message = models.TextField()
    severity = models.CharField(max_length=20, choices=Severity.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="acknowledged_alerts", db_column="acknowledged_by", blank=True, null=True)
    ack_status = models.CharField(max_length=20, choices=AckStatus.choices, default=AckStatus.OPEN)
    resolved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "alerts"
        constraints = [
            models.CheckConstraint(
                condition=(models.Q(ingredient__isnull=False, item__isnull=True) | models.Q(ingredient__isnull=True, item__isnull=False)),
                name="alert_exactly_one_target",
            )
        ]
