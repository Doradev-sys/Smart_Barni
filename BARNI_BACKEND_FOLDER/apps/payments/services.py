from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.audit.services import record as audit_record
from apps.orders.models import Order

from .models import Payment, PaymentProof


WAITSTAFF_ROLES = {"WAITER", "WAITSTAFF"}

DIGITAL_METHODS = {
    Payment.Method.CBE_BIRR,
    Payment.Method.TELEBIRR,
    Payment.Method.BOA,
}


@transaction.atomic
def pay_order(
    *,
    order,
    user,
    method,
    gateway_ref="",
    amount=None,
    proof_image=None,
):
    """
    Record a waiter payment.

    The payment is considered SUCCESS immediately because the waiter
    completes the payment action.

    Digital payments additionally store a screenshot/payment proof
    as evidence for the admin dashboard.

    There is NO admin approval step.
    """

    order = (
        Order.objects
        .select_for_update()
        .get(pk=order.pk)
    )

    # ---------------------------------------------------------
    # Authorization
    # ---------------------------------------------------------

    if user.role_name not in WAITSTAFF_ROLES:
        raise ValueError(
            "Only waitstaff can process payment from this interface."
        )

    if user.branch_id and user.branch_id != order.branch_id:
        raise ValueError("Order belongs to another branch.")

    # ---------------------------------------------------------
    # Order validation
    # ---------------------------------------------------------

    if order.order_type != Order.OrderType.DINE_IN:
        raise ValueError(
            "Online/delivery orders are not paid through the waiter Pay action."
        )

    if order.status not in {
        Order.Status.SENT,
        Order.Status.READY,
        Order.Status.IN_PREP,
    }:
        raise ValueError(
            "This order cannot be paid from its current state."
        )

    if order.waiter_id != user.id:
        raise ValueError(
            "You can only pay your own waiter orders."
        )

    # ---------------------------------------------------------
    # Calculate remaining balance
    # ---------------------------------------------------------

    paid_total = (
        order.payments
        .filter(status=Payment.Status.SUCCESS)
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    remaining = order.total_amount - paid_total

    if remaining <= Decimal("0.00"):
        raise ValueError("Order is already fully paid.")

    amount = (
        remaining
        if amount is None
        else Decimal(amount)
    )

    if amount <= Decimal("0.00"):
        raise ValueError("Payment amount must be greater than zero.")

    if amount > remaining:
        raise ValueError(
            "Payment amount cannot exceed the remaining balance."
        )

    # The waiter Pay action is intentionally for the full balance.
    if amount != remaining:
        raise ValueError(
            "The waiter payment action requires the full remaining "
            "order balance."
        )

    # ---------------------------------------------------------
    # Digital payment validation
    # ---------------------------------------------------------

    is_digital = method in DIGITAL_METHODS

    if is_digital and proof_image is None:
        raise ValueError(
            "A payment proof image is required for digital payments."
        )

    if not is_digital and proof_image is not None:
        raise ValueError(
            "Payment screenshots are only used for digital payments."
        )

    # ---------------------------------------------------------
    # Create successful payment immediately
    # ---------------------------------------------------------

    payment = Payment.objects.create(
        order=order,
        amount=amount,
        method=method,
        gateway_ref=gateway_ref or None,
        status=Payment.Status.SUCCESS,
        paid_at=timezone.now(),
    )

    # ---------------------------------------------------------
    # Store digital payment evidence
    # ---------------------------------------------------------

    proof = None

    if is_digital:
        proof = PaymentProof.objects.create(
            payment=payment,
            image=proof_image,
            submitted_by=user,
        )

    # ---------------------------------------------------------
    # Update order payment method
    # ---------------------------------------------------------

    order.payment_method = method
    order.save(update_fields=["payment_method"])

    # ---------------------------------------------------------
    # Audit
    # ---------------------------------------------------------

    audit_record(
        entity_type="payment",
        entity_id=payment.payment_id,
        action="INSERT",
        new_values={
            "order_id": order.order_id,
            "amount": str(amount),
            "method": method,
            "status": payment.status,
            "paid_at": (
                payment.paid_at.isoformat()
                if payment.paid_at
                else None
            ),
            "payment_proof_id": (
                proof.payment_proof_id
                if proof
                else None
            ),
        },
        user=user,
    )

    return payment, proof, order