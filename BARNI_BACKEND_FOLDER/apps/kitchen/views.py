from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.core.cache import cache
from .models import KitchenOrder
from .serializers import KitchenOrderSerializer, KitchenOrderUpdateSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def kitchen_queue_view(request):
    cache_key = 'kitchen_queue'
    cached = cache.get(cache_key)
    if cached is not None:
        return Response(cached)
    orders = KitchenOrder.objects.select_related('order__menu_item', 'order__table').exclude(status='done')
    data = KitchenOrderSerializer(orders, many=True).data
    cache.set(cache_key, data, 5)
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def kitchen_queue_count_view(request):
    count = KitchenOrder.objects.exclude(status='done').count()
    return Response({'count': count})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def kitchen_history_view(request):
    today = timezone.now().date()
    done = KitchenOrder.objects.select_related('order__menu_item', 'order__table').filter(
        status='done', completed_at__date=today
    )
    data = KitchenOrderSerializer(done, many=True).data
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_kitchen_status_view(request, kitchen_id):
    try:
        k_order = KitchenOrder.objects.get(id=kitchen_id)
    except KitchenOrder.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = KitchenOrderUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    new_status = serializer.validated_data['status']
    k_order.status = new_status
    k_order.notes = serializer.validated_data.get('notes', '')
    if new_status == 'preparing' and not k_order.started_at:
        k_order.started_at = timezone.now()
        k_order.assigned_to = request.user
    elif new_status in ('ready', 'done'):
        k_order.completed_at = timezone.now()
    k_order.save()
    if new_status == 'ready':
        k_order.order.status = 'ready'
        k_order.order.save()
    cache.delete('kitchen_queue')
    return Response(KitchenOrderSerializer(k_order).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_kitchen_entry_view(request, order_id):
    from apps.orders.models import Order
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    if KitchenOrder.objects.filter(order=order).exists():
        return Response({'error': 'Kitchen entry already exists'}, status=status.HTTP_400_BAD_REQUEST)
    kitchen_order = KitchenOrder.objects.create(order=order, status='queued')
    order.status = 'preparing'
    order.save()
    cache.delete('kitchen_queue')
    return Response(KitchenOrderSerializer(kitchen_order).data, status=status.HTTP_201_CREATED)
