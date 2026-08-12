import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("branches", "0001_initial"),
        ("menu", "0001_initial"),
        ("accounts", "0003_srs_role_branch"),
        ("orders", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="Ingredient",
            fields=[
                ("ingredient_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("sku", models.CharField(max_length=40, unique=True)),
                ("name", models.CharField(max_length=120)),
                ("unit_of_measure", models.CharField(max_length=20)),
                ("current_stock", models.DecimalField(decimal_places=4, max_digits=14, validators=[django.core.validators.MinValueValidator(0)])),
                ("reorder_level", models.DecimalField(decimal_places=4, max_digits=14, validators=[django.core.validators.MinValueValidator(0)])),
                ("unit_cost", models.DecimalField(decimal_places=4, max_digits=12, validators=[django.core.validators.MinValueValidator(0)])),
                ("is_processed", models.BooleanField(default=False)),
                ("shelf_life_days", models.IntegerField(blank=True, null=True)),
                ("last_restock_qty", models.DecimalField(blank=True, decimal_places=4, max_digits=14, null=True)),
                ("last_restock_at", models.DateTimeField(blank=True, null=True)),
                ("branch", models.ForeignKey(blank=True, db_column="branch_id", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="ingredients", to="branches.branch")),
            ],
            options={"db_table": "ingredients", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Supplier",
            fields=[
                ("supplier_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=120)),
                ("contact_person", models.CharField(blank=True, max_length=80, null=True)),
                ("phone", models.CharField(blank=True, max_length=20, null=True)),
                ("email", models.CharField(blank=True, max_length=120, null=True)),
                ("address", models.TextField(blank=True, null=True)),
                ("payment_terms", models.CharField(blank=True, max_length=60, null=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"db_table": "suppliers"},
        ),
        migrations.CreateModel(
            name="RecipeBOM",
            fields=[
                ("bom_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("required_qty", models.DecimalField(decimal_places=4, max_digits=12, validators=[django.core.validators.MinValueValidator(0.0001)])),
                ("unit", models.CharField(max_length=20)),
                ("waste_tolerance_pct", models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=5, null=True)),
                ("is_sub_recipe", models.BooleanField(default=False)),
                ("sequence_no", models.IntegerField(blank=True, null=True)),
                ("ingredient", models.ForeignKey(db_column="ingredient_id", on_delete=django.db.models.deletion.PROTECT, related_name="recipe_boms", to="inventory.ingredient")),
                ("item", models.ForeignKey(blank=True, db_column="item_id", null=True, on_delete=django.db.models.deletion.CASCADE, related_name="recipe_boms", to="menu.menuitem")),
                ("parent_bom", models.ForeignKey(blank=True, db_column="parent_bom_id", null=True, on_delete=django.db.models.deletion.CASCADE, related_name="children", to="inventory.recipebom")),
            ],
            options={"db_table": "recipe_bom", "ordering": ["sequence_no", "bom_id"]},
        ),
        migrations.AddConstraint(
            model_name="recipebom",
            constraint=models.CheckConstraint(condition=models.Q(("required_qty__gt", 0)), name="bom_required_qty_positive"),
        ),
        migrations.AddConstraint(
            model_name="recipebom",
            constraint=models.CheckConstraint(condition=models.Q(("waste_tolerance_pct__gte", 0)) & models.Q(("waste_tolerance_pct__lte", 100)), name="bom_waste_pct_valid"),
        ),
        migrations.CreateModel(
            name="StockTransaction",
            fields=[
                ("txn_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("txn_type", models.CharField(choices=[("IN", "In"), ("OUT", "Out"), ("WASTE", "Waste"), ("ADJUSTMENT", "Adjustment")], max_length=20)),
                ("quantity_changed", models.DecimalField(decimal_places=4, max_digits=14)),
                ("balance_after", models.DecimalField(decimal_places=4, max_digits=14)),
                ("unit_cost", models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("reason", models.TextField(blank=True, null=True)),
                ("reference_doc", models.CharField(blank=True, max_length=60, null=True)),
                ("ingredient", models.ForeignKey(db_column="ingredient_id", on_delete=django.db.models.deletion.PROTECT, related_name="stock_transactions", to="inventory.ingredient")),
                ("order", models.ForeignKey(blank=True, db_column="order_id", null=True, on_delete=django.db.models.deletion.PROTECT, related_name="stock_transactions", to="orders.order")),
                ("recorded_by", models.ForeignKey(blank=True, db_column="recorded_by", null=True, on_delete=django.db.models.deletion.PROTECT, related_name="stock_transactions", to="accounts.user")),
                ("supplier", models.ForeignKey(blank=True, db_column="supplier_id", null=True, on_delete=django.db.models.deletion.PROTECT, related_name="stock_transactions", to="inventory.supplier")),
            ],
            options={"db_table": "stock_transactions", "ordering": ["-timestamp"]},
        ),
        migrations.AddIndex(model_name="stocktransaction", index=models.Index(fields=["ingredient", "-timestamp"], name="stock_txn_ing_ts_idx")),
        migrations.AddIndex(model_name="stocktransaction", index=models.Index(fields=["order"], name="stock_txn_order_idx")),
    ]
