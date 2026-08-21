from django.db.models import Q

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.orders.models import Order
from apps.orders.permissions import IsWaitstaff

from .models import Payment, PaymentProof
from .serializers import (
    PayOrderSerializer,
    PaymentSerializer,
    PaymentProofSerializer,
)
from .services import pay_order


class PaymentListView(generics.ListAPIView):
    """
    List payments visible to the current waitstaff user.

    Waitstaff can see:
    - payments for their own dine-in orders
    - delivery payments belonging to their branch
    """

    permission_classes = [
        IsAuthenticated,
        IsWaitstaff,
    ]

    serializer_class = PaymentSerializer

    def get_queryset(self):
        user = self.request.user

        qs = (
            Payment.objects
            .select_related(
                "order",
                "order__branch",
                "order__waiter",
                "order__table",
                "proof",
                "proof__submitted_by",
            )
        )

        if user.branch_id:
            qs = qs.filter(
                order__branch_id=user.branch_id
            )

        return qs.filter(
            Q(order__order_type=Order.OrderType.DELIVERY)
            | Q(order__waiter=user)
        ).distinct()


@api_view(["POST"])
@permission_classes([
    IsAuthenticated,
    IsWaitstaff,
])
def pay_order_view(request, pk):
    """
    Record a payment for a dine-in order.

    Digital payments require a payment screenshot.
    The payment is recorded as SUCCESS immediately.
    """

    order = (
        Order.objects
        .select_related(
            "branch",
            "waiter",
            "table",
        )
        .filter(pk=pk)
        .first()
    )

    if not order:
        return Response(
            {"detail": "Order not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = PayOrderSerializer(
        data=request.data
    )

    serializer.is_valid(
        raise_exception=True
    )

    try:
        payment, proof, updated_order = pay_order(
            order=order,
            user=request.user,
            **serializer.validated_data,
        )

    except ValueError as exc:
        return Response(
            {"detail": str(exc)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {
            "message": "Payment recorded successfully.",
            "payment": PaymentSerializer(payment).data,
            "proof": (
                PaymentProofSerializer(proof).data
                if proof
                else None
            ),
            "order_id": updated_order.order_id,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([
    IsAuthenticated,
    IsWaitstaff,
])
def payment_detail_view(request, pk):
    """
    Retrieve one payment.
    """

    payment = (
        Payment.objects
        .select_related(
            "order",
            "order__branch",
            "order__waiter",
            "order__table",
            "proof",
            "proof__submitted_by",
        )
        .filter(pk=pk)
        .first()
    )

    if not payment:
        return Response(
            {"detail": "Payment not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    order = payment.order
    user = request.user

    if (
        user.branch_id
        and order.branch_id != user.branch_id
    ):
        return Response(
            {"detail": "Payment belongs to another branch."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if (
        order.order_type == Order.OrderType.DINE_IN
        and order.waiter_id != user.id
    ):
        return Response(
            {
                "detail": (
                    "You can only view payments "
                    "for your own waiter orders."
                )
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    return Response(
        PaymentSerializer(payment).data
    )


@api_view(["GET"])
@permission_classes([
    IsAuthenticated,
    IsWaitstaff,
])
def payment_proof_view(request, pk):
    """
    Retrieve payment proof/evidence for a payment.
    """

    proof = (
        PaymentProof.objects
        .select_related(
            "payment",
            "payment__order",
            "payment__order__branch",
            "payment__order__waiter",
            "payment__order__table",
            "submitted_by",
        )
        .filter(payment_id=pk)
        .first()
    )

    if not proof:
        return Response(
            {"detail": "Payment proof not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    order = proof.payment.order
    user = request.user

    if (
        user.branch_id
        and order.branch_id != user.branch_id
    ):
        return Response(
            {"detail": "Payment belongs to another branch."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if (
        order.order_type == Order.OrderType.DINE_IN
        and order.waiter_id != user.id
    ):
        return Response(
            {
                "detail": (
                    "You can only view proof "
                    "for your own waiter orders."
                )
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    return Response(
        PaymentProofSerializer(proof).data
    )
