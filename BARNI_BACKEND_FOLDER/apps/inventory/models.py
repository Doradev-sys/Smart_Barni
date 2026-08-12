from django.core.validators import MinValueValidator
from django.db import models

class Ingredient(models.Model):
    ingredient_id = models.BigAutoField(primary_key=True)
    sku = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=120)
    unit_of_measure = models.CharField(max_length=20)
    current_stock = models.DecimalField(max_digits=14, decimal_places=4, validators=[MinValueValidator(0)])
    reorder_level = models.DecimalField(max_digits=14, decimal_places=4, validators=[MinValueValidator(0)])
    unit_cost = models.DecimalField(max_digits=12, decimal_places=4, validators=[MinValueValidator(0)])
    is_processed = models.BooleanField(default=False)
    shelf_life_days = models.IntegerField(blank=True, null=True)
    last_restock_qty = models.DecimalField(max_digits=14, decimal_places=4, blank=True, null=True)
    last_restock_at = models.DateTimeField(blank=True, null=True)
    branch = models.ForeignKey("branches.Branch", on_delete=models.SET_NULL, related_name="ingredients", db_column="branch_id", blank=True, null=True)

    class Meta:
        db_table = "ingredients"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.sku})"

class RecipeBOM(models.Model):
    bom_id = models.BigAutoField(primary_key=True)
    item = models.ForeignKey("menu.MenuItem", on_delete=models.CASCADE, related_name="recipe_boms", db_column="item_id", blank=True, null=True)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT, related_name="recipe_boms", db_column="ingredient_id")
    required_qty = models.DecimalField(max_digits=12, decimal_places=4, validators=[MinValueValidator(0.0001)])
    unit = models.CharField(max_length=20)
    waste_tolerance_pct = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, default=0)
    is_sub_recipe = models.BooleanField(default=False)
    parent_bom = models.ForeignKey("self", on_delete=models.CASCADE, related_name="children", db_column="parent_bom_id", blank=True, null=True)
    sequence_no = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "recipe_bom"
        ordering = ["sequence_no", "bom_id"]
        constraints = [
            models.CheckConstraint(condition=models.Q(required_qty__gt=0), name="bom_required_qty_positive"),
            models.CheckConstraint(condition=models.Q(waste_tolerance_pct__gte=0) & models.Q(waste_tolerance_pct__lte=100), name="bom_waste_pct_valid"),
        ]

class StockTransaction(models.Model):
    class TxnType(models.TextChoices):
        IN = "IN", "In"
        OUT = "OUT", "Out"
        WASTE = "WASTE", "Waste"
        ADJUSTMENT = "ADJUSTMENT", "Adjustment"

    txn_id = models.BigAutoField(primary_key=True)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT, related_name="stock_transactions", db_column="ingredient_id")
    order = models.ForeignKey("orders.Order", on_delete=models.PROTECT, related_name="stock_transactions", db_column="order_id", blank=True, null=True)
    supplier = models.ForeignKey("inventory.Supplier", on_delete=models.PROTECT, related_name="stock_transactions", db_column="supplier_id", blank=True, null=True)
    txn_type = models.CharField(max_length=20, choices=TxnType.choices)
    quantity_changed = models.DecimalField(max_digits=14, decimal_places=4)
    balance_after = models.DecimalField(max_digits=14, decimal_places=4)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="stock_transactions", db_column="recorded_by", blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    reference_doc = models.CharField(max_length=60, blank=True, null=True)

    class Meta:
        db_table = "stock_transactions"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["ingredient", "-timestamp"], name="stock_txn_ing_ts_idx"),
            models.Index(fields=["order"], name="stock_txn_order_idx"),
        ]

class Supplier(models.Model):
    supplier_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=120)
    contact_person = models.CharField(max_length=80, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=120, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    payment_terms = models.CharField(max_length=60, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = "suppliers"

