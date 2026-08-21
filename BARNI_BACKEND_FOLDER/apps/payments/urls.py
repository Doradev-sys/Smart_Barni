from django.urls import path

from .views import (
    PaymentListView,
    pay_order_view,
    payment_detail_view,
    payment_proof_view,
)


urlpatterns = [
    path(
        "orders/<int:pk>/pay/",
        pay_order_view,
        name="pay-order",
    ),

    path(
        "records/",
        PaymentListView.as_view(),
        name="payment-records",
    ),

    path(
        "<int:pk>/",
        payment_detail_view,
        name="payment-detail",
    ),

    path(
        "<int:pk>/proof/",
        payment_proof_view,
        name="payment-proof",
    ),
]
