from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Q
from .models import Order, Receipt, Table
from .serializers import OrderSerializer, ReceiptSerializer, TableSerializer, OrderCreateSerializer
from apps.menu.models import MenuItem
import random
import string


def make_order_id():
    num = random.randint(10, 99)
    letter = random.choice(string.ascii_lowercase)
    return f"#{num}{letter}"


def make_receipt_number():
    num = random.randint(1000, 9999)
    letter = random.choice(string.ascii_lowercase)
    return f"R{num}{letter}"


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related('menu_item', 'table', 'customer', 'waiter').all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        source = self.request.query_params.get('source')
        if status_filter:
            qs = qs.filter(status=status_filter)
        if source:
            qs = qs.filter(source=source)
        return qs


class ReceiptViewSet(viewsets.ModelViewSet):
    queryset = Receipt.objects.select_related('order', 'waiter').all()
    serializer_class = ReceiptSerializer
    permission_classes = [IsAuthenticated]


class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [IsAuthenticated]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order_view(request):
    serializer = OrderCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    try:
        menu_item = MenuItem.objects.get(id=data['menu_item_id'])
    except MenuItem.DoesNotExist:
        return Response({'error': 'Menu item not found'}, status=status.HTTP_404_NOT_FOUND)
    order_id = make_order_id()
    total = menu_item.price * data['quantity']
    table = None
    if data.get('table_id'):
        try:
            table = Table.objects.get(number=data['table_id'])
        except Table.DoesNotExist:
            pass
    order = Order.objects.create(
        order_id=order_id,
        menu_item=menu_item,
        table=table,
        customer=request.user if request.user.role == 'Customer' else None,
        side=data.get('side', 'Plain'),
        quantity=data['quantity'],
        total=total,
        source=data.get('source', 'barni'),
        payment_method=data.get('payment_method', ''),
        qr_data=data.get('qr_data', ''),
        notes=data.get('notes', ''),
        status='preparing',
    )
    from apps.kitchen.models import KitchenOrder
    KitchenOrder.objects.create(order=order, status='queued', assigned_to=request.user)
    from django.core.cache import cache
    cache.delete('kitchen_queue')
    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def customer_place_order_view(request):
    serializer = OrderCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    try:
        menu_item = MenuItem.objects.get(id=data['menu_item_id'])
    except MenuItem.DoesNotExist:
        return Response({'error': 'Menu item not found'}, status=status.HTTP_404_NOT_FOUND)
    order_id = make_order_id()
    total = menu_item.price * data['quantity']
    order = Order.objects.create(
        order_id=order_id,
        menu_item=menu_item,
        customer=request.user,
        side=data.get('side', 'Plain'),
        quantity=data['quantity'],
        total=total,
        source='customer',
        payment_method=data.get('payment_method', ''),
        qr_data=data.get('qr_data', ''),
    )
    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_order_view(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    order.status = 'preparing'
    order.waiter = request.user
    order.save()
    from apps.kitchen.models import KitchenOrder
    if not KitchenOrder.objects.filter(order=order).exists():
        KitchenOrder.objects.create(order=order, status='queued', assigned_to=request.user)
    from django.core.cache import cache
    cache.delete('kitchen_queue')
    return Response(OrderSerializer(order).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_order_view(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    order.status = 'cancelled'
    order.save()
    return Response(OrderSerializer(order).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pay_order_view(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    method = request.data.get('payment_method', 'Cash')
    qr_data = request.data.get('qr_data', '')
    receipt_number = make_receipt_number()
    receipt = Receipt.objects.create(
        receipt_number=receipt_number,
        order=order,
        waiter=request.user,
        table_label=f"Table {order.table.number}" if order.table else ('Online order' if order.source == 'online' else ''),
        item_label=f"{order.menu_item.name} ({order.side})" if order.menu_item else '',
        quantity=order.quantity,
        total=order.total,
        payment_method=method,
        qr_data=qr_data,
        printed=True,
    )
    order.status = 'served'
    order.payment_method = method
    if qr_data:
        order.qr_data = qr_data
    order.save()
    return Response(ReceiptSerializer(receipt).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_orders_view(request):
    orders = Order.objects.filter(customer=request.user).select_related('menu_item', 'table').order_by('-created_at')
    return Response(OrderSerializer(orders, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_order_count_view(request):
    count = Order.objects.filter(customer=request.user).exclude(status__in=['served', 'declined', 'cancelled']).count()
    return Response({'count': count})


@api_view(['GET'])
@permission_classes([AllowAny])
def tables_view(request):
    tables = Table.objects.filter(is_active=True)
    return Response(TableSerializer(tables, many=True).data)
