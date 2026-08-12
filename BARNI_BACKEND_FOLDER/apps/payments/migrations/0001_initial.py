import django.core.validators
import django.db.models.deletion
from django.db import migrations, models
from apps.payments.models import payment_proof_upload_path


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("accounts", "0003_srs_role_branch"),
        ("orders", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("payment_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0.01)])),
                ("method", models.CharField(choices=[("CASH", "Cash"), ("CARD", "Card"), ("TELEBIRR", "Telebirr"), ("CBE_BIRR", "CBE Birr"), ("BOA", "BOA"), ("OTHER", "Other")], max_length=30)),
                ("gateway_ref", models.CharField(blank=True, max_length=100, null=True)),
                ("status", models.CharField(choices=[("PENDING", "Pending"), ("SUCCESS", "Success"), ("FAILED", "Failed"), ("REFUNDED", "Refunded")], default="PENDING", max_length=20)),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("order", models.ForeignKey(db_column="order_id", on_delete=django.db.models.deletion.PROTECT, related_name="payments", to="orders.order")),
            ],
            options={"db_table": "payments", "ordering": ["-payment_id"]},
        ),
        migrations.AddIndex(model_name="payment", index=models.Index(fields=["order", "status"], name="payments_order_status_idx")),
        migrations.CreateModel(
            name="PaymentProof",
            fields=[
                ("payment_proof_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("image", models.ImageField(upload_to=payment_proof_upload_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"])])),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
                ("verification_status", models.CharField(choices=[("PENDING", "Pending verification"), ("APPROVED", "Approved"), ("REJECTED", "Rejected")], default="PENDING", max_length=20)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("review_note", models.TextField(blank=True, null=True)),
                ("payment", models.OneToOneField(db_column="payment_id", on_delete=django.db.models.deletion.PROTECT, related_name="proof", to="payments.payment")),
                ("reviewed_by", models.ForeignKey(blank=True, db_column="reviewed_by", null=True, on_delete=django.db.models.deletion.PROTECT, related_name="reviewed_payment_proofs", to="accounts.user")),
                ("submitted_by", models.ForeignKey(db_column="submitted_by", on_delete=django.db.models.deletion.PROTECT, related_name="submitted_payment_proofs", to="accounts.user")),
            ],
            options={"db_table": "payment_proofs", "ordering": ["-submitted_at"]},
        ),
        migrations.AddIndex(model_name="paymentproof", index=models.Index(fields=["verification_status", "submitted_at"], name="payment_proof_status_idx")),
    ]
