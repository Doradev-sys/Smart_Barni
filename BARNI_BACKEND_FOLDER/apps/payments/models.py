from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from decimal import Decimal

def payment_proof_upload_path(instance, filename):
    return f"payment_proofs/{instance.payment.order_id}/{instance.payment_id}/{filename}"

class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = "CASH", "Cash"
        CARD = "CARD", "Card"
        TELEBIRR = "TELEBIRR", "Telebirr"
        CBE_BIRR = "CBE_BIRR", "CBE Birr"
        BOA = "BOA", "BOA"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"

    payment_id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(
        "orders.Order", on_delete=models.PROTECT, related_name="payments", db_column="order_id"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    method = models.CharField(max_length=30, choices=Method.choices)
    gateway_ref = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    paid_at = models.DateTimeField(blank=True, null=True)
    class Meta:
        db_table = "payments"
        ordering = ["-payment_id"]
        indexes = [models.Index(fields=["order", "status"])]

    def __str__(self):
        return f"Payment {self.payment_id} / Order {self.order_id} / {self.amount}"


class PaymentProof(models.Model):
    """Stored evidence for manually verified digital/transfer payments.

    This is intentionally separate from Receipt: a screenshot proves a payment;
    the receipt is a generated view of Order + OrderItem + Payment + proof metadata.
    """

    class VerificationStatus(models.TextChoices):
        PENDING = "PENDING", "Pending verification"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    payment_proof_id = models.BigAutoField(primary_key=True)
    payment = models.OneToOneField(
        Payment, on_delete=models.PROTECT, related_name="proof", db_column="payment_id"
    )
    image = models.ImageField(
        upload_to=payment_proof_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"])],
    )
    submitted_by = models.ForeignKey(
        "accounts.User", on_delete=models.PROTECT, related_name="submitted_payment_proofs",
        db_column="submitted_by"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    verification_status = models.CharField(
        max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.PENDING
    )
    reviewed_by = models.ForeignKey(
        "accounts.User", on_delete=models.PROTECT, related_name="reviewed_payment_proofs",
        db_column="reviewed_by", blank=True, null=True
    )
    reviewed_at = models.DateTimeField(blank=True, null=True)
    review_note = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "payment_proofs"
        ordering = ["-submitted_at"]
        indexes = [models.Index(fields=["verification_status", "submitted_at"])]

    def __str__(self):
        return f"Payment proof {self.payment_proof_id} / Payment {self.payment_id}"
