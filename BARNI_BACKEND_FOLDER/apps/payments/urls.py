from django.urls import path
from .views import (
    pay_order_view, pending_payment_proofs_view,
    approve_payment_proof_view, reject_payment_proof_view,
)

urlpatterns = [
    path("orders/<int:pk>/pay/", pay_order_view, name="pay-order"),
    path("proofs/pending/", pending_payment_proofs_view, name="pending-payment-proofs"),
    path("proofs/<int:proof_id>/approve/", approve_payment_proof_view, name="approve-payment-proof"),
    path("proofs/<int:proof_id>/reject/", reject_payment_proof_view, name="reject-payment-proof"),
]
