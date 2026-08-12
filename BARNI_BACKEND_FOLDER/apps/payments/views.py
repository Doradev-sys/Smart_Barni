from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.orders.models import Order
from apps.orders.permissions import IsWaitstaff
from apps.orders.serializers import OrderSerializer
from apps.orders.services import receipt_projection
from .models import Payment, PaymentProof
from .serializers import PayOrderSerializer, PaymentProofSerializer, PaymentSerializer
from .services import pay_order, approve_payment_proof, reject_payment_proof


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsWaitstaff])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def pay_order_view(request, pk):
    order = Order.objects.select_related("waiter", "branch", "table").prefetch_related("items__item", "payments__proof").filter(pk=pk).first()
    if not order:
        return Response({"detail": "Order not found."}, status=404)
    serializer = PayOrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        payment, proof, order = pay_order(order=order, user=request.user, **serializer.validated_data)
    except ValueError as exc:
        return Response({"detail": str(exc)}, status=400)
    return Response({
        "payment": PaymentSerializer(payment).data,
        "order": OrderSerializer(order).data,
        "receipt": receipt_projection(order, request),
        "payment_action": "AWAITING_ADMIN_VERIFICATION" if proof else "ACCEPTED",
    }, status=201)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def pending_payment_proofs_view(request):
    if request.user.role_name not in {"OWNER", "ADMIN", "OWNER_ADMIN", "SYSTEM_ADMIN", "MANAGER"}:
        return Response({"detail": "Only an administrator/manager can view payment proofs."}, status=403)
    proofs = PaymentProof.objects.filter(
        verification_status=PaymentProof.VerificationStatus.PENDING
    ).select_related("payment", "payment__order", "submitted_by")
    if request.user.branch_id:
        proofs = proofs.filter(payment__order__branch_id=request.user.branch_id)
    return Response(PaymentProofSerializer(proofs, many=True, context={"request": request}).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def approve_payment_proof_view(request, proof_id):
    proof = PaymentProof.objects.select_related("payment", "payment__order").filter(pk=proof_id).first()
    if not proof:
        return Response({"detail": "Payment proof not found."}, status=404)
    if request.user.branch_id and proof.payment.order.branch_id != request.user.branch_id:
        return Response({"detail": "Payment proof belongs to another branch."}, status=403)
    try:
        payment, proof, order = approve_payment_proof(proof=proof, reviewer=request.user)
    except ValueError as exc:
        return Response({"detail": str(exc)}, status=400)
    return Response({
        "payment": PaymentSerializer(payment).data,
        "proof": PaymentProofSerializer(proof, context={"request": request}).data,
        "order": OrderSerializer(order).data,
        "receipt": receipt_projection(order, request),
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reject_payment_proof_view(request, proof_id):
    proof = PaymentProof.objects.select_related("payment", "payment__order").filter(pk=proof_id).first()
    if not proof:
        return Response({"detail": "Payment proof not found."}, status=404)
    if request.user.branch_id and proof.payment.order.branch_id != request.user.branch_id:
        return Response({"detail": "Payment proof belongs to another branch."}, status=403)
    note = str(request.data.get("note", "")).strip()
    if not note:
        return Response({"note": "A rejection reason is required."}, status=400)
    try:
        payment, proof = reject_payment_proof(proof=proof, reviewer=request.user, note=note)
    except ValueError as exc:
        return Response({"detail": str(exc)}, status=400)
    return Response({
        "payment": PaymentSerializer(payment).data,
        "proof": PaymentProofSerializer(proof, context={"request": request}).data,
        "message": "Payment proof rejected. The waiter can submit a new payment proof."
    })
