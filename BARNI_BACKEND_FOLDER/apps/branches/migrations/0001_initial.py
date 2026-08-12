import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Branch",
            fields=[
                ("branch_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
                ("address", models.TextField(blank=True, null=True)),
                ("phone", models.CharField(blank=True, max_length=20, null=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"db_table": "branches", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="DiningTable",
            fields=[
                ("table_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("table_number", models.CharField(max_length=20)),
                ("capacity", models.PositiveIntegerField(blank=True, null=True)),
                ("status", models.CharField(choices=[("FREE", "Free"), ("OCCUPIED", "Occupied"), ("RESERVED", "Reserved"), ("CLEANING", "Cleaning")], default="FREE", max_length=20)),
                ("location", models.CharField(blank=True, max_length=50, null=True)),
                ("branch", models.ForeignKey(db_column="branch_id", on_delete=django.db.models.deletion.PROTECT, related_name="dining_tables", to="branches.branch")),
            ],
            options={"db_table": "dining_tables", "ordering": ["branch_id", "table_number"]},
        ),
        migrations.AddConstraint(
            model_name="diningtable",
            constraint=models.UniqueConstraint(fields=("branch", "table_number"), name="uq_dining_table_branch_number"),
        ),
    ]
