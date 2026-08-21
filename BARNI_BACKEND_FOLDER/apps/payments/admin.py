from django.contrib import admin

from .models import Payment, PaymentProof


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "payment_id",
        "order",
        "amount",
        "method",
        "status",
        "paid_at",
    )

    list_filter = (
        "method",
        "status",
    )

    search_fields = (
        "payment_id",
        "order__order_id",
        "order__table__table_id",
        "order__waiter__username",
        "gateway_ref",
    )

    readonly_fields = (
        "payment_id",
        "paid_at",
    )


@admin.register(PaymentProof)
class PaymentProofAdmin(admin.ModelAdmin):
    """
    Payment proofs are evidence only.

    They are NOT approved or rejected from this admin interface.
    """

    list_display = (
        "payment_proof_id",
        "payment",
        "order_id",
        "table_id",
        "waiter_id",
        "submitted_by",
        "submitted_at",
    )

    search_fields = (
        "payment__order__order_id",
        "payment__order__table__table_id",
        "payment__order__waiter__username",
        "payment__gateway_ref",
        "submitted_by__username",
    )

    readonly_fields = (
        "payment_proof_id",
        "payment",
        "image",
        "submitted_by",
        "submitted_at",
    )

    @admin.display(
        description="Order ID",
        ordering="payment__order__order_id",
    )
    def order_id(self, obj):
        return obj.payment.order_id

    @admin.display(
        description="Table ID",
        ordering="payment__order__table_id",
    )
    def table_id(self, obj):
        return obj.payment.order.table_id

    @admin.display(
        description="Waiter ID",
        ordering="payment__order__waiter_id",
    )
    def waiter_id(self, obj):
        return obj.payment.order.waiter_id