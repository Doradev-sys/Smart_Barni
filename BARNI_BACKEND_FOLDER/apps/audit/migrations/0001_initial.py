import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [("accounts", "0003_srs_role_branch")]
    operations = [
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("log_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("entity_type", models.CharField(max_length=40)),
                ("entity_id", models.BigIntegerField(blank=True, null=True)),
                ("action", models.CharField(max_length=30)),
                ("old_values", models.JSONField(blank=True, null=True)),
                ("new_values", models.JSONField(blank=True, null=True)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(blank=True, db_column="user_id", null=True, on_delete=django.db.models.deletion.PROTECT, related_name="audit_logs", to="accounts.user")),
            ],
            options={"db_table": "audit_log", "ordering": ["-created_at"]},
        ),
        migrations.AddIndex(model_name="auditlog", index=models.Index(fields=["entity_type", "entity_id", "created_at"], name="audit_entity_idx")),
    ]
