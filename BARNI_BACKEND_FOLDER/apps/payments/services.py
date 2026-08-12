from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from apps.orders.models import Order
from apps.audit.services import record as audit_record
from .models import Payment, PaymentProof

WAITSTAFF_ROLES = {"WAITER", "WAITSTAFF"}
PAYMENT_VERIFIER_ROLES = {"OWNER", "ADMIN", "OWNER_ADMIN", "SYSTEM_ADMIN", "MANAGER"}
DIGITAL_METHODS = {Payment.Method.CBE_BIRR, Payment.Method.TELEBIRR, Payment.Method.BOA}


def _assert_verifier(user):
    if user.role_name not in PAYMENT_VERIFIER_ROLES:
        raise ValueError("Only an administrator/manager can verify payment proof.")


@transaction.atomic
def pay_order(*, order, user, method, gateway_ref="", amount=None, proof_image=None):
    order = Order.objects.select_for_update().get(pk=order.pk)
    if user.role_name not in WAITSTAFF_ROLES:
        raise ValueError("Only waitstaff can process payment from this interface.")
    if user.branch_id and user.branch_id != order.branch_id:
        raise ValueError("Order belongs to another branch.")
    if order.order_type != Order.OrderType.DINE_IN:
        raise ValueError("Online/delivery orders are not paid through the waiter Pay action.")
    if order.status not in {Order.Status.SENT, Order.Status.READY, Order.Status.IN_PREP}:
        raise ValueError("This order cannot be paid from its current state.")
    if order.waiter_id != user.id:
        raise ValueError("You can only pay your own waiter orders.")

    from django.db.models import Sum
    paid_total = order.payments.filter(status=Payment.Status.SUCCESS).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    pending_exists = order.payments.filter(status=Payment.Status.PENDING).exists()
    if pending_exists:
        raise ValueError("This order already has a payment awaiting verification.")
    remaining = order.total_amount - paid_total
    if remaining <= Decimal("0.00"):
        raise ValueError("Order is already fully paid.")
    amount = remaining if amount is None else Decimal(amount)
    if amount > remaining:
        raise ValueError("Payment amount cannot exceed the remaining balance.")
    if amount != remaining:
        raise ValueError("The waiter payment action requires the full remaining order balance.")

    is_digital = method in DIGITAL_METHODS
    if is_digital and proof_image is None:
        raise ValueError("A payment proof image is required for digital payments.")

    payment = Payment.objects.create(
        order=order,
        amount=amount,
        method=method,
        gateway_ref=gateway_ref or None,
        status=Payment.Status.PENDING if is_digital else Payment.Status.SUCCESS,
        paid_at=None if is_digital else timezone.now(),
    )

    proof = None
    if is_digital:
        proof = PaymentProof.objects.create(
            payment=payment, image=proof_image, submitted_by=user
        )
    if amount == remaining:
        order.payment_method = method
        order.save(update_fields=["payment_method"])

    audit_record(
        entity_type="payment",
        entity_id=payment.payment_id,
        action="INSERT",
        new_values={
            "order_id": order.order_id,
            "amount": str(amount),
            "method": method,
            "status": payment.status,
            "payment_proof_id": proof.payment_proof_id if proof else None,
        },
        user=user,
    )
    return payment, proof, order


@transaction.atomic
def approve_payment_proof(*, proof, reviewer):
    _assert_verifier(reviewer)
    proof = PaymentProof.objects.select_for_update().select_related("payment", "payment__order").get(pk=proof.pk)
    if proof.verification_status != PaymentProof.VerificationStatus.PENDING:
        raise ValueError("This payment proof has already been reviewed.")

    payment = Payment.objects.select_for_update().get(pk=proof.payment_id)
    if payment.status != Payment.Status.PENDING:
        raise ValueError("This payment is no longer awaiting verification.")

    order = Order.objects.select_for_update().get(pk=payment.order_id)
    payment.status = Payment.Status.SUCCESS
    payment.paid_at = timezone.now()
    payment.save(update_fields=["status", "paid_at"])
    order.payment_method = payment.method
    order.save(update_fields=["payment_method"])

    proof.verification_status = PaymentProof.VerificationStatus.APPROVED
    proof.reviewed_by = reviewer
    proof.reviewed_at = timezone.now()
    proof.save(update_fields=["verification_status", "reviewed_by", "reviewed_at"])
    audit_record(
        entity_type="payment_proof", entity_id=proof.payment_proof_id, action="OVERRIDE",
        old_values={"verification_status": PaymentProof.VerificationStatus.PENDING, "payment_status": Payment.Status.PENDING},
        new_values={"verification_status": PaymentProof.VerificationStatus.APPROVED, "payment_status": Payment.Status.SUCCESS},
        user=reviewer,
    )
    return payment, proof, order


@transaction.atomic
def reject_payment_proof(*, proof, reviewer, note):
    _assert_verifier(reviewer)
    proof = PaymentProof.objects.select_for_update().select_related("payment").get(pk=proof.pk)
    if proof.verification_status != PaymentProof.VerificationStatus.PENDING:
        raise ValueError("This payment proof has already been reviewed.")

    payment = Payment.objects.select_for_update().get(pk=proof.payment_id)
    if payment.status != Payment.Status.PENDING:
        raise ValueError("This payment is no longer awaiting verification.")

    payment.status = Payment.Status.FAILED
    payment.save(update_fields=["status"])
    proof.verification_status = PaymentProof.VerificationStatus.REJECTED
    proof.reviewed_by = reviewer
    proof.reviewed_at = timezone.now()
    proof.review_note = note
    proof.save(update_fields=["verification_status", "reviewed_by", "reviewed_at", "review_note"])
    audit_record(
        entity_type="payment_proof", entity_id=proof.payment_proof_id, action="OVERRIDE",
        old_values={"verification_status": PaymentProof.VerificationStatus.PENDING, "payment_status": Payment.Status.PENDING},
        new_values={"verification_status": PaymentProof.VerificationStatus.REJECTED, "payment_status": Payment.Status.FAILED, "review_note": note},
        user=reviewer,
    )
    return payment, proof
