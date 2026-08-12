import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("accounts", "0003_srs_role_branch"),
        ("inventory", "0001_initial"),
        ("menu", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="Alert",
            fields=[
                ("alert_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("alert_type", models.CharField(choices=[("LOW_STOCK", "Low stock"), ("MISSING_INGREDIENT", "Missing ingredient"), ("WASTAGE", "Wastage"), ("UNPROFITABLE", "Unprofitable"), ("VARIANCE", "Variance")], max_length=40)),
                ("message", models.TextField()),
                ("severity", models.CharField(choices=[("INFO", "Info"), ("WARNING", "Warning"), ("CRITICAL", "Critical")], max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("ack_status", models.CharField(choices=[("OPEN", "Open"), ("ACKNOWLEDGED", "Acknowledged"), ("RESOLVED", "Resolved")], default="OPEN", max_length=20)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                ("acknowledged_by", models.ForeignKey(blank=True, db_column="acknowledged_by", null=True, on_delete=django.db.models.deletion.PROTECT, related_name="acknowledged_alerts", to="accounts.user")),
                ("ingredient", models.ForeignKey(blank=True, db_column="ingredient_id", null=True, on_delete=django.db.models.deletion.PROTECT, related_name="alerts", to="inventory.ingredient")),
                ("item", models.ForeignKey(blank=True, db_column="item_id", null=True, on_delete=django.db.models.deletion.PROTECT, related_name="alerts", to="menu.menuitem")),
            ],
            options={"db_table": "alerts"},
        ),
        migrations.AddConstraint(
            model_name="alert",
            constraint=models.CheckConstraint(
                condition=(models.Q(("ingredient__isnull", False), ("item__isnull", True)) | models.Q(("ingredient__isnull", True), ("item__isnull", False))),
                name="alert_exactly_one_target",
            ),
        ),
    ]
