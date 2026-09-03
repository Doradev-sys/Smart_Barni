from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum
from .models import Payment
from .serializers import PaymentSerializer
from apps.accounts.permissions import IsAdmin
from apps.orders.models import Order
from apps.orders.serializers import OrderSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_payment_view(request):
    serializer = PaymentSerializer(data=request.data)
    if serializer.is_valid():
        payment = serializer.save(user=request.user, status='completed')
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# ADMIN REFUND VIEW
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_refund_order_view(request, order_id):
    """
    Admin manually refund an order
    POST /api/payments/admin/orders/{order_id}/refund/
    """
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response(
            {'detail': 'Order not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if order is paid
    if order.payment_status != 'paid':
        return Response(
            {'detail': 'Order is not paid. Cannot refund.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update payment status
    Payment.objects.filter(order=order).update(status='refunded')
    
    # Update order payment status
    order.payment_status = 'refunded'
    order.status = 'cancelled'
    order.save()
    
    # Update kitchen
    try:
        from apps.kitchen.models import KitchenOrder
        KitchenOrder.objects.filter(order=order).update(status='cancelled')
    except ImportError:
        pass
    
    return Response({
        'detail': 'Order refunded successfully',
        'order': OrderSerializer(order).data
    }, status=status.HTTP_200_OK)