from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.utils import timezone

from apps.branches.models import DiningTable
from apps.inventory.services import InsufficientStock, deduct_for_order, reverse_order_stock
from apps.audit.services import record as audit_record
from .models import Order

VAT_RATE = Decimal("0.15")
ACTIVE_TABLE_STATUSES = {Order.Status.OPEN, Order.Status.SENT, Order.Status.IN_PREP, Order.Status.READY, Order.Status.SERVED}


def _release_table_if_free(table):
    if not table:
        return
    exists = Order.objects.filter(table=table, status__in=ACTIVE_TABLE_STATUSES).exists()
    if not exists and table.status != DiningTable.Status.FREE:
        table.status = DiningTable.Status.FREE
        table.save(update_fields=["status"])


def receipt_projection(order, request=None):
    payments = list(order.payments.select_related("proof").order_by("payment_id"))
    latest_payment = payments[-1] if payments else None

    def proof_projection(payment):
        proof = getattr(payment, "proof", None) if payment else None
        if not proof:
            return None
        image_url = proof.image.url if proof.image else None
        if request is not None and image_url:
            image_url = request.build_absolute_uri(image_url)
        return {
            "id": proof.payment_proof_id,
            "verification_status": proof.verification_status,
            "image_url": image_url,
            "submitted_at": proof.submitted_at.isoformat() if proof.submitted_at else None,
            "reviewed_at": proof.reviewed_at.isoformat() if proof.reviewed_at else None,
            "review_note": proof.review_note,
        }

    return {
        "order_id": order.order_id,
        "table_number": order.table.table_number if order.table else None,
        "waiter_name": order.waiter.full_name if order.waiter else None,
        "items": [
            {
                "name": line.item.name,
                "quantity": str(line.quantity),
                "unit_price": str(line.unit_price),
                "line_total": str(line.line_total),
            }
            for line in order.items.select_related("item").all()
        ],
        "subtotal": str(order.subtotal),
        "tax_amount": str(order.tax_amount),
        "total_amount": str(order.total_amount),
        "payment_method": latest_payment.method if latest_payment else order.payment_method,
        "payment_status": (
            "SUCCESS" if latest_payment and latest_payment.status == "SUCCESS" and all(p.status == "SUCCESS" for p in payments)
            else latest_payment.status if latest_payment else "UNPAID"
        ),
        "paid_at": latest_payment.paid_at.isoformat() if latest_payment and latest_payment.paid_at else None,
        "payments": [
            {
                "payment_id": payment.payment_id,
                "amount": str(payment.amount),
                "method": payment.method,
                "gateway_ref": payment.gateway_ref,
                "status": payment.status,
                "paid_at": payment.paid_at.isoformat() if payment.paid_at else None,
                "proof": proof_projection(payment),
            }
            for payment in payments
        ],
        "payment_proof": proof_projection(latest_payment),
        "order_timestamp": order.order_timestamp.isoformat(),
        "status": order.status,
    }


class OrderService:
    @staticmethod
    @transaction.atomic
    def create_waiter_order(*, waiter, branch, table, items, notes=""):
        if waiter.role_name not in {"WAITER", "WAITSTAFF"}:
            raise ValueError("Only waitstaff can create waiter orders.")
        if waiter.branch_id is None:
            raise ValueError("A waiter must be assigned to a branch before creating orders.")
        if waiter.branch_id != branch.pk:
            raise ValueError("Waiter is assigned to a different branch.")
        table = DiningTable.objects.select_for_update().get(pk=table.pk)
        if table.branch_id != branch.pk or table.status != DiningTable.Status.FREE:
            raise ValueError("Selected table is not free in this branch.")

        order = Order.objects.create(
            branch=branch,
            table=table,
            waiter=waiter,
            order_type=Order.OrderType.DINE_IN,
            status=Order.Status.SENT,
            notes=notes or None,
        )
        subtotal = Decimal("0.00")
        for data in items:
            from apps.menu.models import MenuItem
            item = MenuItem.objects.select_for_update().select_related("category").get(pk=data["menu_item_id"])
            if not item.is_active or not item.category.is_active:
                raise ValueError(f"Menu item '{item.name}' is unavailable.")
            quantity = Decimal(data["quantity"])
            line_total = (item.selling_price * quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            OrderItem.objects.create(
                order=order,
                item=item,
                quantity=quantity,
                unit_price=item.selling_price,
                line_total=line_total,
                kitchen_station=item.kitchen_station,
                notes=data.get("notes") or None,
                sent_to_kitchen_at=timezone.now(),
            )
            subtotal += line_total
        tax = (subtotal * VAT_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total = subtotal + tax
        order.subtotal = subtotal
        order.tax_amount = tax
        order.total_amount = total
        order.save(update_fields=["subtotal", "tax_amount", "total_amount"])

        # The DB-SRS requires a Recipe_BOM before an item can be sold and an OUT ledger
        # transaction for the resulting leaf ingredients. Roll back the whole order on failure.
        try:
            deduct_for_order(order=order, recorded_by=waiter)
        except InsufficientStock as exc:
            raise ValueError(str(exc)) from exc

        table.status = DiningTable.Status.OCCUPIED
        table.save(update_fields=["status"])
        audit_record(
            entity_type="order",
            entity_id=order.order_id,
            action="INSERT",
            new_values={
                "branch_id": branch.pk,
                "table_id": table.pk,
                "waiter_id": waiter.pk,
                "status": order.status,
                "total_amount": str(order.total_amount),
            },
            user=waiter,
        )
        return order

    @staticmethod
    @transaction.atomic
    def cancel_order(*, order, user):
        order = Order.objects.select_for_update().get(pk=order.pk)
        if order.order_type != Order.OrderType.DINE_IN:
            raise ValueError("Only waiter dine-in orders can be cancelled here.")
        if order.waiter_id != user.id:
            raise ValueError("You can only cancel your own waiter orders.")
        if order.status != Order.Status.SENT:
            raise ValueError("Only SENT waiter orders can be cancelled.")
        if order.payments.filter(status="SUCCESS").exists():
            raise ValueError("A paid order cannot be cancelled from the waiter interface.")
        if order.payments.filter(status="PENDING").exists():
            raise ValueError("Resolve the pending digital payment before cancelling the order.")

        old_status = order.status
        reverse_order_stock(order=order, recorded_by=user)
        order.status = Order.Status.CANCELLED
        order.closed_at = timezone.now()
        order.save(update_fields=["status", "closed_at"])
        audit_record(
            entity_type="order",
            entity_id=order.order_id,
            action="VOID",
            old_values={"status": old_status},
            new_values={"status": Order.Status.CANCELLED},
            user=user,
        )
        _release_table_if_free(order.table)
        return order

    @staticmethod
    @transaction.atomic
    def serve_online_order(*, order, user):
        order = Order.objects.select_for_update().get(pk=order.pk)
        if order.order_type != Order.OrderType.DELIVERY:
            raise ValueError("Only online/delivery orders can be served from this action.")
        if order.status != Order.Status.READY:
            raise ValueError("Only READY online orders can be served.")
        if user.branch_id and user.branch_id != order.branch_id:
            raise ValueError("Order belongs to another branch.")
        order.status = Order.Status.SERVED
        order.save(update_fields=["status"])
        return order

    @staticmethod
    @transaction.atomic
    def complete_order(*, order, user):
        order = Order.objects.select_for_update().get(pk=order.pk)
        if user.branch_id and user.branch_id != order.branch_id:
            raise ValueError("Order belongs to another branch.")
        if order.order_type == Order.OrderType.DINE_IN:
            if order.waiter_id != user.id:
                raise ValueError("You can only finish your own waiter orders.")
            from django.db.models import Sum
            paid_total = order.payments.filter(status="SUCCESS").aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
            if paid_total < order.total_amount:
                raise ValueError("The waiter order must be fully paid before it can be finished.")
            if order.status not in {Order.Status.SENT, Order.Status.SERVED, Order.Status.READY}:
                raise ValueError("This waiter order cannot be finished from its current state.")
        elif order.order_type == Order.OrderType.DELIVERY:
            if order.status != Order.Status.SERVED:
                raise ValueError("Online order must be served before it is finished.")
        else:
            raise ValueError("This order type is not supported by the waiter completion action.")
        order.status = Order.Status.CLOSED
        order.closed_at = timezone.now()
        order.save(update_fields=["status", "closed_at"])
        _release_table_if_free(order.table)
        return order
