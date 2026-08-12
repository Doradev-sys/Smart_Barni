import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("accounts", "0003_srs_role_branch"),
        ("branches", "0001_initial"),
        ("menu", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                ("order_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("order_timestamp", models.DateTimeField(auto_now_add=True)),
                ("status", models.CharField(choices=[("OPEN", "Open"), ("SENT", "Sent"), ("IN_PREP", "In preparation"), ("READY", "Ready"), ("SERVED", "Served"), ("CLOSED", "Closed"), ("CANCELLED", "Cancelled")], default="OPEN", max_length=30)),
                ("order_type", models.CharField(choices=[("DINE_IN", "Dine in"), ("DELIVERY", "Delivery"), ("TAKEAWAY", "Takeaway")], max_length=20)),
                ("subtotal", models.DecimalField(decimal_places=2, default=0, max_digits=12, validators=[django.core.validators.MinValueValidator(0)])),
                ("tax_amount", models.DecimalField(decimal_places=2, default=0, max_digits=12, validators=[django.core.validators.MinValueValidator(0)])),
                ("total_amount", models.DecimalField(decimal_places=2, default=0, max_digits=12, validators=[django.core.validators.MinValueValidator(0)])),
                ("payment_method", models.CharField(blank=True, max_length=30, null=True)),
                ("notes", models.TextField(blank=True, null=True)),
                ("closed_at", models.DateTimeField(blank=True, null=True)),
                ("branch", models.ForeignKey(db_column="branch_id", on_delete=django.db.models.deletion.PROTECT, related_name="orders", to="branches.branch")),
                ("customer", models.ForeignKey(blank=True, db_column="customer_id", null=True, on_delete=django.db.models.deletion.PROTECT, related_name="customer_orders", to="accounts.user")),
                ("table", models.ForeignKey(blank=True, db_column="table_id", null=True, on_delete=django.db.models.deletion.PROTECT, related_name="orders", to="branches.diningtable")),
                ("waiter", models.ForeignKey(blank=True, db_column="waiter_id", null=True, on_delete=django.db.models.deletion.PROTECT, related_name="waiter_orders", to="accounts.user")),
            ],
            options={"db_table": "orders", "ordering": ["-order_timestamp"]},
        ),
        migrations.AddIndex(model_name="order", index=models.Index(fields=["branch", "-order_timestamp"], name="orders_branch_ts_idx")),
        migrations.AddIndex(model_name="order", index=models.Index(fields=["waiter", "-order_timestamp"], name="orders_waiter_ts_idx")),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("order_item_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("quantity", models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(0.01)])),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0)])),
                ("line_total", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0)])),
                ("prep_status", models.CharField(choices=[("QUEUED", "Queued"), ("IN_PREP", "In preparation"), ("READY", "Ready"), ("SERVED", "Served"), ("VOID", "Void")], default="QUEUED", max_length=20)),
                ("kitchen_station", models.CharField(blank=True, max_length=40, null=True)),
                ("notes", models.TextField(blank=True, null=True)),
                ("sent_to_kitchen_at", models.DateTimeField(blank=True, null=True)),
                ("ready_at", models.DateTimeField(blank=True, null=True)),
                ("item", models.ForeignKey(db_column="item_id", on_delete=django.db.models.deletion.PROTECT, related_name="order_items", to="menu.menuitem")),
                ("order", models.ForeignKey(db_column="order_id", on_delete=django.db.models.deletion.PROTECT, related_name="items", to="orders.order")),
            ],
            options={"db_table": "order_items", "ordering": ["order_item_id"]},
        ),
        migrations.AddIndex(model_name="orderitem", index=models.Index(fields=["prep_status"], name="order_items_prep_idx")),
    ]
