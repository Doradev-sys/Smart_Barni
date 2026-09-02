# apps/orders/views.py
# ============================================================================
# COMPLETE VIEWS FILE WITH PAYMENT VIEWS
# ============================================================================

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Q
from django.core.cache import cache
from .models import Order, Receipt, Table, OrderItem
from .serializers import (
    OrderSerializer, ReceiptSerializer, TableSerializer, OrderCreateSerializer,
    CustomerOrderCreateSerializer, CustomerOrderSerializer
)
from apps.menu.models import MenuItem
from apps.accounts.permissions import IsCustomer
from apps.payments.serializers import PaymentSerializer
import random
import string


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def make_order_id():
    """Generate a unique order ID"""
    num = random.randint(10, 99)
    letter = random.choice(string.ascii_lowercase)
    return f"#{num}{letter}"


def make_receipt_number():
    """Generate a unique receipt number"""
    num = random.randint(1000, 9999)
    letter = random.choice(string.ascii_lowercase)
    return f"R{num}{letter}"


# ============================================================================
# VIEWSETS
# ============================================================================

class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for Order CRUD operations"""
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
    """ViewSet for Receipt CRUD operations"""
    queryset = Receipt.objects.select_related('order', 'waiter').all()
    serializer_class = ReceiptSerializer
    permission_classes = [IsAuthenticated]


class TableViewSet(viewsets.ModelViewSet):
    """ViewSet for Table CRUD operations"""
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [IsAuthenticated]


# ============================================================================
# STAFF/ADMIN ORDER VIEWS
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order_view(request):
    """
    Place an order (staff)
    POST /api/orders/place/
    """
    serializer = OrderCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    try:
        menu_item = MenuItem.objects.get(id=data['menu_item_id'])
    except MenuItem.DoesNotExist:
        return Response({'error': 'Menu item not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if not menu_item.is_available:
        return Response({'error': f'{menu_item.name} is not available'}, status=status.HTTP_400_BAD_REQUEST)
    
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
        status='pending',
    )
    
    try:
        from apps.kitchen.models import KitchenOrder
        KitchenOrder.objects.create(order=order, status='queued')
    except ImportError:
        pass
    
    cache.delete('kitchen_queue')
    
    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_order_view(request, order_id):
    """
    Accept an order (staff only)
    POST /api/orders/{order_id}/accept/
    """
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if order.status != 'pending':
        return Response(
            {'error': f'Order cannot be accepted. Current status: {order.status}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    order.status = 'preparing'
    order.waiter = request.user
    order.save()
    
    try:
        from apps.kitchen.models import KitchenOrder
        kitchen_order, created = KitchenOrder.objects.get_or_create(order=order)
        kitchen_order.status = 'preparing'
        kitchen_order.assigned_to = request.user
        kitchen_order.save()
    except ImportError:
        pass
    
    cache.delete('kitchen_queue')
    
    return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_order_view(request, order_id):
    """
    Cancel an order (staff only)
    POST /api/orders/{order_id}/cancel/
    """
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if order.status in ['served', 'declined', 'cancelled']:
        return Response(
            {'error': f'Order cannot be cancelled. Current status: {order.status}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    order.status = 'cancelled'
    order.save()
    
    try:
        from apps.kitchen.models import KitchenOrder
        KitchenOrder.objects.filter(order=order).update(status='cancelled')
    except ImportError:
        pass
    
    cache.delete('kitchen_queue')
    
    return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pay_order_view(request, order_id):
    """
    Pay for an order and create receipt (staff)
    POST /api/orders/{order_id}/pay/
    """
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if order.status in ['served', 'declined', 'cancelled']:
        return Response(
            {'error': f'Order cannot be paid. Current status: {order.status}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
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


# ============================================================================
# CUSTOMER ORDER VIEWS
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def customer_place_order_view(request):
    """
    Place a single-item order from a customer
    POST /api/orders/customer/place/
    """
    serializer = OrderCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    try:
        menu_item = MenuItem.objects.get(id=data['menu_item_id'])
    except MenuItem.DoesNotExist:
        return Response({'error': 'Menu item not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if not menu_item.is_available:
        return Response({'error': f'{menu_item.name} is not available'}, status=status.HTTP_400_BAD_REQUEST)
    
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
        source='customer',
        payment_method=data.get('payment_method', ''),
        qr_data=data.get('qr_data', ''),
        notes=data.get('notes', ''),
        status='pending',
    )
    
    try:
        from apps.kitchen.models import KitchenOrder
        KitchenOrder.objects.create(order=order, status='queued')
    except ImportError:
        pass
    
    cache.delete('kitchen_queue')
    
    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_orders_view(request):
    """
    Get all orders for the authenticated customer (legacy)
    GET /api/orders/customer/my-orders/
    """
    orders = Order.objects.filter(
        customer=request.user
    ).select_related('menu_item', 'table').order_by('-created_at')
    
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_order_count_view(request):
    """
    Get count of active orders for the customer
    GET /api/orders/customer/count/
    """
    count = Order.objects.filter(
        customer=request.user
    ).exclude(
        status__in=['served', 'declined', 'cancelled']
    ).count()
    
    return Response({'count': count})


@api_view(['GET'])
@permission_classes([AllowAny])
def tables_view(request):
    """
    Get list of all active tables
    GET /api/orders/tables/
    """
    tables = Table.objects.filter(is_active=True)
    serializer = TableSerializer(tables, many=True)
    return Response(serializer.data)


# ============================================================================
# ENHANCED CUSTOMER ORDER VIEWS
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsCustomer])
@transaction.atomic
def customer_create_order_view(request):
    """
    Create an order with multiple items
    POST /api/orders/customer/orders/create/
    """
    serializer = CustomerOrderCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    items_data = data['items']
    
    # Calculate totals
    subtotal = 0
    order_items = []
    
    for item_data in items_data:
        try:
            menu_item = MenuItem.objects.get(id=item_data['menu_item_id'])
            quantity = item_data['quantity']
            price = menu_item.price
            item_subtotal = price * quantity
            subtotal += item_subtotal
            
            order_items.append({
                'menu_item': menu_item,
                'quantity': quantity,
                'price': price,
                'subtotal': item_subtotal,
                'notes': item_data.get('notes', '')
            })
        except MenuItem.DoesNotExist:
            return Response(
                {'error': f"Menu item {item_data['menu_item_id']} not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    # Calculate tax (10%)
    tax = subtotal * Decimal('0.10')
    
    # Calculate delivery fee if applicable
    delivery_fee = 0
    if data.get('order_type') == 'delivery':
        delivery_fee = 5.00
    
    total = subtotal + tax + delivery_fee
    
    # Get table if provided
    table = None
    if data.get('table_number'):
        try:
            table = Table.objects.get(number=data['table_number'], is_active=True)
        except Table.DoesNotExist:
            pass
    
    # Generate order ID
    order_id = make_order_id()
    
    # Create the order
    order = Order.objects.create(
        order_id=order_id,
        customer=request.user,
        subtotal=subtotal,
        tax=tax,
        total=total,
        delivery_fee=delivery_fee,
        order_type=data.get('order_type', 'dine_in'),
        delivery_address=data.get('delivery_address', ''),
        table=table,
        notes=data.get('notes', ''),
        status='pending',
        source='customer',
        payment_method=data.get('payment_method', ''),
        payment_status='pending',
    )
    
    # Create order items
    for item in order_items:
        OrderItem.objects.create(
            order=order,
            menu_item=item['menu_item'],
            quantity=item['quantity'],
            price=item['price'],
            subtotal=item['subtotal'],
            notes=item['notes']
        )
    
    # Send to kitchen
    try:
        from apps.kitchen.models import KitchenOrder
        KitchenOrder.objects.create(order=order, status='queued')
    except ImportError:
        pass
    
    # Clear cache
    cache.delete('kitchen_queue')
    
    return Response(CustomerOrderSerializer(order).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsCustomer])
def customer_orders_history_view(request):
    """
    Get all orders for the authenticated customer
    GET /api/orders/customer/orders/
    """
    orders = Order.objects.filter(
        customer=request.user
    ).prefetch_related('items__menu_item').order_by('-created_at')
    
    serializer = CustomerOrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsCustomer])
def customer_order_detail_view(request, order_id):
    """
    Get details of a specific order
    GET /api/orders/customer/orders/{order_id}/
    """
    try:
        order = Order.objects.get(id=order_id, customer=request.user)
    except Order.DoesNotExist:
        return Response(
            {'detail': 'Order not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = CustomerOrderSerializer(order)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsCustomer])
def customer_cancel_order_view(request, order_id):
    """
    Cancel an order
    POST /api/orders/customer/orders/{order_id}/cancel/
    """
    try:
        order = Order.objects.get(id=order_id, customer=request.user)
    except Order.DoesNotExist:
        return Response(
            {'detail': 'Order not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Only allow cancellation if order is pending or preparing
    if order.status not in ['pending', 'preparing']:
        return Response(
            {'detail': f'Order cannot be cancelled. Current status: {order.status}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    order.status = 'cancelled'
    order.save()
    
    # Update kitchen order
    try:
        from apps.kitchen.models import KitchenOrder
        KitchenOrder.objects.filter(order=order).update(status='cancelled')
    except ImportError:
        pass
    
    # Clear cache
    cache.delete('kitchen_queue')
    
    return Response(CustomerOrderSerializer(order).data)


# ============================================================================
# PAYMENT VIEWS (NEW)
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsCustomer])
def customer_pay_order_view(request, order_id):
    """
    Pay for an order
    POST /api/orders/customer/orders/{order_id}/pay/
    """
    from decimal import Decimal
    from apps.payments.models import Payment
    
    try:
        order = Order.objects.get(id=order_id, customer=request.user)
    except Order.DoesNotExist:
        return Response(
            {'detail': 'Order not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if order can be paid
    if order.status in ['cancelled', 'declined']:
        return Response(
            {'detail': f'Order cannot be paid. Status: {order.status}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if order.payment_status == 'paid':
        return Response(
            {'detail': 'Order already paid'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get payment details from request
    method = request.data.get('method', 'Cash')
    email = request.data.get('email', '')
    phone = request.data.get('phone', '')
    account_number = request.data.get('account_number', '')
    qr_data = request.data.get('qr_data', '')
    reference = request.data.get('reference', '')
    
    # Create payment record
    payment = Payment.objects.create(
        order=order,
        user=request.user,
        method=method,
        amount=order.total,
        status='completed',
        reference=reference,
        qr_data=qr_data,
        account_number=account_number,
        email=email,
        phone=phone,
    )
    
    # Update order payment status
    order.payment_status = 'paid'
    order.payment_method = method
    order.status = 'preparing'
    order.save()
    
    # Create receipt
    from .models import Receipt
    receipt_number = f"R{random.randint(1000,9999)}{random.choice(string.ascii_lowercase)}"
    
    receipt = Receipt.objects.create(
        receipt_number=receipt_number,
        order=order,
        waiter=request.user,
        table_label=f"Table {order.table.number}" if order.table else 'Online Order',
        item_label=f"Order {order.order_id}",
        quantity=1,
        total=order.total,
        payment_method=method,
        qr_data=qr_data,
        printed=True,
    )
    
    return Response({
        'order': CustomerOrderSerializer(order).data,
        'payment': PaymentSerializer(payment).data,
        'receipt': ReceiptSerializer(receipt).data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsCustomer])
def customer_payment_history_view(request):
    """
    Get payment history for the customer
    GET /api/orders/customer/payments/
    """
    from apps.payments.models import Payment
    from apps.payments.serializers import PaymentSerializer
    
    payments = Payment.objects.filter(
        user=request.user
    ).select_related('order').order_by('-created_at')
    
    serializer = PaymentSerializer(payments, many=True)
    return Response(serializer.data)