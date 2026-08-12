from collections import defaultdict
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.alerts.models import Alert
from .models import Ingredient, RecipeBOM, StockTransaction


class InsufficientStock(Exception):
    pass


def _leaf_requirements(item, quantity):
    """Resolve a menu item's Recipe_BOM to raw ingredient quantities.

    Supports the explicit parent_bom_id nesting model finalized in the SRS.
    A processed ingredient must therefore appear as a parent Recipe_BOM row with
    child rows linked through parent_bom_id.
    """
    result = defaultdict(Decimal)
    roots = list(
        RecipeBOM.objects.filter(item=item, parent_bom__isnull=True)
        .select_related("ingredient")
    )
    if not roots:
        raise ValueError(f"Menu item '{item.name}' has no Recipe_BOM and cannot be sold.")

    def add_waste(qty, row):
        pct = row.waste_tolerance_pct or Decimal("0")
        return qty * (Decimal("1") + Decimal(pct) / Decimal("100"))

    def walk(row, multiplier, path):
        if row.bom_id in path:
            raise ValueError("Recipe cycle detected in Recipe_BOM hierarchy.")
        path = path | {row.bom_id}
        factor = add_waste(Decimal(row.required_qty) * multiplier, row)

        children = list(
            RecipeBOM.objects.filter(parent_bom=row)
            .select_related("ingredient")
        )
        if children:
            for child in children:
                walk(child, factor, path)
            return

        ingredient = row.ingredient
        if row.unit.strip().lower() != ingredient.unit_of_measure.strip().lower():
            raise ValueError(
                f"Recipe_BOM unit '{row.unit}' does not match ingredient unit "
                f"'{ingredient.unit_of_measure}' for '{ingredient.name}'."
            )
        if ingredient.is_processed:
            # A processed ingredient is only sellable here when its BOM is
            # represented by explicit parent_bom_id children. The SRS
            # recommends this explicit tree because a pure item=NULL BOM
            # header has no direct owner FK to identify which processed
            # ingredient it belongs to.
            raise ValueError(
                f"Processed ingredient '{ingredient.name}' must be represented "
                "as an explicit nested Recipe_BOM tree with parent_bom_id."
            )

        result[ingredient.ingredient_id] += factor

    for root in roots:
        walk(root, Decimal(quantity), set())
    return result


@transaction.atomic
def deduct_for_order(*, order, recorded_by):
    """Atomically deduct recipe leaf ingredients for a confirmed order."""
    required = defaultdict(Decimal)
    for line in order.items.select_related("item"):
        for ingredient_id, qty in _leaf_requirements(line.item, line.quantity).items():
            required[ingredient_id] += qty

    ingredients = {
        i.ingredient_id: i
        for i in Ingredient.objects.select_for_update().filter(
            ingredient_id__in=required.keys()
        )
    }
    for ingredient_id, qty in required.items():
        ingredient = ingredients.get(ingredient_id)
        if ingredient is None:
            raise ValueError(f"Ingredient {ingredient_id} no longer exists.")
        if ingredient.current_stock < qty:
            raise InsufficientStock(
                f"Insufficient stock for {ingredient.name}: required {qty} "
                f"{ingredient.unit_of_measure}, available {ingredient.current_stock}."
            )

    for ingredient_id, qty in required.items():
        ingredient = ingredients[ingredient_id]
        ingredient.current_stock -= qty
        ingredient.save(update_fields=["current_stock"])
        StockTransaction.objects.create(
            ingredient=ingredient,
            order=order,
            txn_type=StockTransaction.TxnType.OUT,
            quantity_changed=-qty,
            balance_after=ingredient.current_stock,
            unit_cost=ingredient.unit_cost,
            timestamp=timezone.now(),
            recorded_by=recorded_by,
            reason="Menu sale",
        )
        if ingredient.current_stock <= ingredient.reorder_level:
            already_open = Alert.objects.filter(
                alert_type="LOW_STOCK",
                ingredient=ingredient,
                ack_status=Alert.AckStatus.OPEN,
            ).exists()
            if not already_open:
                Alert.objects.create(
                    alert_type="LOW_STOCK",
                    ingredient=ingredient,
                    message=(
                        f"Low stock: {ingredient.name} has {ingredient.current_stock} "
                        f"{ingredient.unit_of_measure} remaining."
                    ),
                    severity=Alert.Severity.WARNING,
                    ack_status=Alert.AckStatus.OPEN,
                )
    return True


@transaction.atomic
def reverse_order_stock(*, order, recorded_by):
    """Post compensating ADJUSTMENT ledger entries when a sold order is cancelled."""
    out_transactions = list(
        StockTransaction.objects.select_for_update()
        .filter(order=order, txn_type=StockTransaction.TxnType.OUT)
        .select_related("ingredient")
    )
    if not out_transactions:
        return False

    ingredient_ids = {txn.ingredient_id for txn in out_transactions}
    ingredients = {
        i.ingredient_id: i
        for i in Ingredient.objects.select_for_update().filter(
            ingredient_id__in=ingredient_ids
        )
    }
    for txn in out_transactions:
        ingredient = ingredients[txn.ingredient_id]
        restore_qty = abs(Decimal(txn.quantity_changed))
        ingredient.current_stock += restore_qty
        ingredient.save(update_fields=["current_stock"])
        StockTransaction.objects.create(
            ingredient=ingredient,
            order=order,
            txn_type=StockTransaction.TxnType.ADJUSTMENT,
            quantity_changed=restore_qty,
            balance_after=ingredient.current_stock,
            unit_cost=ingredient.unit_cost,
            timestamp=timezone.now(),
            recorded_by=recorded_by,
            reason="Order cancellation stock reversal",
            reference_doc=f"ORDER-{order.order_id}-CANCEL",
        )
        if ingredient.current_stock > ingredient.reorder_level:
            Alert.objects.filter(
                alert_type="LOW_STOCK",
                ingredient=ingredient,
                ack_status=Alert.AckStatus.OPEN,
            ).update(
                ack_status=Alert.AckStatus.RESOLVED,
                resolved_at=timezone.now(),
            )
    return True
