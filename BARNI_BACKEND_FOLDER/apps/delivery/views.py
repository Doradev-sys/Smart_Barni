# apps/delivery/views.py
# ============================================================================
# COMPLETE DELIVERY VIEWS WITH CUSTOMER TRACKING
# ============================================================================

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Delivery
from .serializers import DeliverySerializer
from apps.accounts.permissions import IsCustomer
from apps.orders.models import Order


class DeliveryViewSet(viewsets.ModelViewSet):
    """ViewSet for Delivery CRUD operations (Staff/Admin only)"""
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]


# ============================================================================
# CUSTOMER DELIVERY TRACKING VIEWS
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsCustomer])
def customer_track_delivery_view(request, order_id):
    """
    Track delivery status for a customer's order
    GET /api/delivery/customer/track/{order_id}/
    """
    try:
        # Verify the order belongs to the customer
        order = Order.objects.get(id=order_id, customer=request.user)
    except Order.DoesNotExist:
        return Response(
            {'detail': 'Order not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if delivery exists for this order
    try:
        delivery = Delivery.objects.get(order=order)
    except Delivery.DoesNotExist:
        return Response(
            {'detail': 'Delivery not yet assigned to this order'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get driver name
    driver_name = delivery.driver.username if delivery.driver else 'Not assigned'
    
    # Return delivery tracking info
    return Response({
        'order_id': order.order_id,
        'order_status': order.status,
        'delivery': {
            'id': delivery.id,
            'status': delivery.status,
            'driver': driver_name,
            'address': delivery.address,
            'phone': delivery.phone,
            'notes': delivery.notes,
            'created_at': delivery.created_at,
            'updated_at': delivery.updated_at,
        },
        'tracking_info': {
            'status_display': delivery.get_status_display(),
            'estimated_delivery_time': order.estimated_delivery_time,
            'is_delivered': delivery.status == 'delivered',
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsCustomer])
def customer_delivery_history_view(request):
    """
    Get all deliveries for the authenticated customer
    GET /api/delivery/customer/history/
    """
    # Get all orders for the customer that have deliveries
    orders = Order.objects.filter(customer=request.user)
    deliveries = Delivery.objects.filter(order__in=orders).select_related('order', 'driver')
    
    # Prepare response
    result = []
    for delivery in deliveries:
        result.append({
            'order_id': delivery.order.order_id,
            'order_status': delivery.order.status,
            'delivery_status': delivery.status,
            'driver': delivery.driver.username if delivery.driver else 'Not assigned',
            'address': delivery.address,
            'phone': delivery.phone,
            'created_at': delivery.created_at,
            'updated_at': delivery.updated_at,
            'is_delivered': delivery.status == 'delivered',
        })
    
    return Response({
        'count': len(result),
        'deliveries': result
    }, status=status.HTTP_200_OK)


# ============================================================================
# DRIVER DELIVERY VIEWS (Optional)
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def driver_deliveries_view(request):
    """
    Get deliveries assigned to the current driver
    GET /api/delivery/driver/assigned/
    """
    if request.user.role not in ['Driver', 'Admin']:
        return Response(
            {'detail': 'Only drivers can access this endpoint'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    deliveries = Delivery.objects.filter(
        driver=request.user
    ).exclude(
        status='delivered'
    ).select_related('order')
    
    serializer = DeliverySerializer(deliveries, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_delivery_status_view(request, delivery_id):
    """
    Update delivery status (Driver/Admin only)
    POST /api/delivery/driver/update/{delivery_id}/
    """
    if request.user.role not in ['Driver', 'Admin']:
        return Response(
            {'detail': 'Only drivers or admins can update delivery status'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        delivery = Delivery.objects.get(id=delivery_id)
    except Delivery.DoesNotExist:
        return Response(
            {'detail': 'Delivery not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if driver is assigned to this delivery
    if delivery.driver and delivery.driver != request.user:
        return Response(
            {'detail': 'You are not assigned to this delivery'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    new_status = request.data.get('status')
    if not new_status:
        return Response(
            {'detail': 'Status is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    valid_statuses = ['pending', 'assigned', 'picked_up', 'delivered', 'cancelled']
    if new_status not in valid_statuses:
        return Response(
            {'detail': f'Invalid status. Must be one of: {valid_statuses}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update delivery status
    delivery.status = new_status
    delivery.save()
    
    # If delivered, update order status too
    if new_status == 'delivered':
        delivery.order.status = 'served'
        delivery.order.save()
    
    return Response({
        'message': f'Delivery status updated to {new_status}',
        'delivery': DeliverySerializer(delivery).data
    }, status=status.HTTP_200_OK)