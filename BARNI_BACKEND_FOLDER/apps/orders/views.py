from django.db.models import Q
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .permissions import IsWaitstaff
from .serializers import (
    CreateWaiterOrderSerializer, OrderSerializer, OrderRowSerializer,
    ReportIssueSerializer, OrderIssueSerializer, OrderSummarySerializer,
)
from .services import OrderService, receipt_projection, report_order_issue, order_summary
from .models import Order, OrderIssue


class OrderListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsWaitstaff]
    def get_serializer_class(self):
        return CreateWaiterOrderSerializer if self.request.method == "POST" else OrderSerializer
    def get_queryset(self):
        qs = Order.objects.select_related("branch", "waiter", "customer", "table").prefetch_related("items__item", "payments__proof")
        branch_id = self.request.query_params.get("branch_id")
        ui_status = self.request.query_params.get("status")
        order_type = self.request.query_params.get("order_type")
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        if order_type == "ONLINE":
            qs = qs.filter(order_type=Order.OrderType.DELIVERY)
        elif order_type:
            qs = qs.filter(order_type=order_type)
        if ui_status == "ORDERED":
            qs = qs.filter(status=Order.Status.SENT).exclude(
                payments__status__in=["SUCCESS", "PENDING"]
            )
        elif ui_status == "ONLINE":
            qs = qs.filter(order_type=Order.OrderType.DELIVERY, status=Order.Status.READY)
        elif ui_status == "PAID":
            qs = qs.filter(payments__status="SUCCESS", status__in=[Order.Status.SENT, Order.Status.READY, Order.Status.SERVED])
        elif ui_status == "COMPLETED":
            qs = qs.filter(status=Order.Status.CLOSED)
        elif ui_status:
            qs = qs.filter(status=ui_status)
        if self.request.user.branch_id:
            qs = qs.filter(branch_id=self.request.user.branch_id)
        # Waiters see their own dine-in orders plus branch online/delivery orders.
        return qs.filter(Q(order_type=Order.OrderType.DELIVERY) | Q(waiter=self.request.user)).distinct()
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

@api_view(["POST"])
@permission_classes([IsAuthenticated, IsWaitstaff])
def cancel_order_view(request, pk):
    order = Order.objects.select_related("waiter", "table").prefetch_related("payments").filter(pk=pk).first()
    if not order:
        return Response({"detail": "Order not found."}, status=404)
    try:
        order = OrderService.cancel_order(order=order, user=request.user)
    except ValueError as exc:
        return Response({"detail": str(exc)}, status=400)
    return Response(OrderSerializer(order).data)

@api_view(["POST"])
@permission_classes([IsAuthenticated, IsWaitstaff])
def serve_order_view(request, pk):
    order = Order.objects.select_related("branch", "table").filter(pk=pk).first()
    if not order:
        return Response({"detail": "Order not found."}, status=404)
    try:
        order = OrderService.serve_online_order(order=order, user=request.user)
    except ValueError as exc:
        return Response({"detail": str(exc)}, status=400)
    return Response({"order": OrderSerializer(order).data, "receipt": receipt_projection(order, request)})

@api_view(["POST"])
@permission_classes([IsAuthenticated, IsWaitstaff])
def complete_order_view(request, pk):
    order = Order.objects.select_related("branch", "table", "waiter").prefetch_related("items__item", "payments__proof").filter(pk=pk).first()
    if not order:
        return Response({"detail": "Order not found."}, status=404)
    try:
        order = OrderService.complete_order(order=order, user=request.user)
    except ValueError as exc:
        return Response({"detail": str(exc)}, status=400)
    return Response({"order": OrderSerializer(order).data, "receipt": receipt_projection(order, request)})

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsWaitstaff])
def receipt_view(request, pk):
    order = Order.objects.select_related("branch", "table", "waiter").prefetch_related(
        "items__item", "payments__proof"
    ).filter(pk=pk).first()
    if not order:
        return Response({"detail": "Order not found."}, status=404)
    if request.user.branch_id and order.branch_id != request.user.branch_id:
        return Response({"detail": "Order belongs to another branch."}, status=403)
    if order.order_type == Order.OrderType.DINE_IN and order.waiter_id != request.user.id:
        return Response({"detail": "You can only view receipts for your own waiter orders."}, status=403)
    return Response(receipt_projection(order, request))
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsWaitstaff])
def order_summary_view(request):
    branch_id = request.query_params.get("branch_id") or request.user.branch_id
    date_from = request.query_params.get("date_from")
    date_to = request.query_params.get("date_to")
    data = order_summary(branch_id=branch_id, date_from=date_from, date_to=date_to)
    return Response(OrderSummarySerializer(data).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsWaitstaff])
def report_issue_view(request, pk):
    order = Order.objects.filter(pk=pk).first()
    if not order:
        return Response({"detail": "Order not found."}, status=404)
    serializer = ReportIssueSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        issue = report_order_issue(order=order, reported_by=request.user, **serializer.validated_data)
    except ValueError as exc:
        return Response({"detail": str(exc)}, status=400)
    return Response(OrderIssueSerializer(issue).data, status=status.HTTP_201_CREATED)