import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("category_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=80)),
                ("cuisine_type", models.CharField(blank=True, max_length=50, null=True)),
                ("meal_period", models.CharField(blank=True, choices=[("BREAKFAST", "Breakfast"), ("LUNCH", "Lunch"), ("DINNER", "Dinner"), ("ALL_DAY", "All day")], max_length=30, null=True)),
                ("display_order", models.IntegerField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"db_table": "categories", "ordering": ["display_order", "name"]},
        ),
        migrations.CreateModel(
            name="MenuItem",
            fields=[
                ("item_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=120)),
                ("description", models.TextField(blank=True, null=True)),
                ("selling_price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("labor_pct", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ("rent_pct", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ("utility_pct", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ("kitchen_station", models.CharField(blank=True, max_length=40, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("image_url", models.CharField(blank=True, max_length=255, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("category", models.ForeignKey(db_column="category_id", on_delete=django.db.models.deletion.PROTECT, related_name="menu_items", to="menu.category")),
            ],
            options={"db_table": "menu_items", "ordering": ["category_id", "name"]},
        ),
        migrations.AddConstraint(
            model_name="menuitem",
            constraint=models.CheckConstraint(condition=models.Q(("selling_price__gte", 0)), name="menu_item_selling_price_nonnegative"),
        ),
    ]
