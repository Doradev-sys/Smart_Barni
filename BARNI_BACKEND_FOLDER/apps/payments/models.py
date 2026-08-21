from decimal import Decimal

from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models


def payment_proof_upload_path(instance, filename):
    return (
        f"payment_proofs/"
        f"{instance.payment.order_id}/"
        f"{instance.payment_id}/"
        f"{filename}"
    )


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
        "orders.Order",
        on_delete=models.PROTECT,
        related_name="payments",
        db_column="order_id",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    method = models.CharField(
        max_length=30,
        choices=Method.choices,
    )

    gateway_ref = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    paid_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "payments"
        ordering = ["-payment_id"]
        indexes = [
            models.Index(fields=["order", "status"]),
        ]

    def __str__(self):
        return (
            f"Payment {self.payment_id} / "
            f"Order {self.order_id} / {self.amount}"
        )


class PaymentProof(models.Model):
    """
    Evidence attached to a digital/transfer payment.

    PaymentProof is NOT an approval workflow.

    The waiter submits the payment and the proof together.
    The payment is already recorded as SUCCESS.
    The proof simply provides evidence for the admin dashboard.
    """

    payment_proof_id = models.BigAutoField(primary_key=True)

    payment = models.OneToOneField(
        Payment,
        on_delete=models.PROTECT,
        related_name="proof",
        db_column="payment_id",
    )

    image = models.ImageField(
        upload_to=payment_proof_upload_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp"]
            )
        ],
    )

    submitted_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="submitted_payment_proofs",
        db_column="submitted_by",
    )

    submitted_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        db_table = "payment_proofs"
        ordering = ["-submitted_at"]
        indexes = [
            models.Index(fields=["submitted_at"]),
        ]

    def __str__(self):
        return (
            f"Payment proof {self.payment_proof_id} / "
            f"Payment {self.payment_id}"
        )