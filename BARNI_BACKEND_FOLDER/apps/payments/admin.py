from django.contrib import admin
from .models import Payment, PaymentProof

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("payment_id", "order", "amount", "method", "status", "paid_at", "processed_by")
    list_filter = ("method", "status")
    search_fields = ("payment_id", "order__order_id", "gateway_ref")

@admin.register(PaymentProof)
class PaymentProofAdmin(admin.ModelAdmin):
    list_display = ("payment_proof_id", "payment", "verification_status", "submitted_by", "submitted_at", "reviewed_by", "reviewed_at")
    list_filter = ("verification_status",)
    search_fields = ("payment__order__order_id", "payment__gateway_ref", "submitted_by__username")
    readonly_fields = ("submitted_at", "reviewed_at")
