from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from apps.orders.models import Order, Receipt


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def daily_report_view(request):
    date_str = request.query_params.get('date')
    if date_str:
        try:
            day = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            day = timezone.now().date()
    else:
        day = timezone.now().date()
    orders_today = Order.objects.filter(created_at__date=day)
    receipts_today = Receipt.objects.filter(created_at__date=day)
    total_revenue = receipts_today.aggregate(total=Sum('total'))['total'] or 0
    total_orders = orders_today.count()
    served = orders_today.filter(status='served').count()
    declined = orders_today.filter(status='declined').count()
    return Response({
        'date': str(day),
        'total_orders': total_orders,
        'served_orders': served,
        'declined_orders': declined,
        'total_revenue': float(total_revenue),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def waiter_reports_view(request):
    date_str = request.query_params.get('date')
    if date_str:
        try:
            day = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            day = timezone.now().date()
    else:
        day = timezone.now().date()
    reports = Receipt.objects.filter(created_at__date=day).order_by('-created_at')
    data = []
    for r in reports:
        data.append({
            'orderId': str(r.order.id) if r.order else '',
            'name': r.item_label,
            'table': r.table_label,
            'orderType': 'Online' if 'Online' in r.table_label else 'At Barni',
            'payment': r.payment_method,
            'time': r.created_at.strftime('%H:%M'),
            'price': float(r.total),
            'declined': False,
            'qrData': r.qr_data or '',
        })
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def kitchen_reports_view(request):
    from apps.kitchen.models import KitchenOrder
    date_str = request.query_params.get('date')
    if date_str:
        try:
            day = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            day = timezone.now().date()
    else:
        day = timezone.now().date()
    done = KitchenOrder.objects.filter(completed_at__date=day, status='done')
    data = []
    for k in done:
        data.append({
            'orderId': str(k.order.order_id) if k.order else '',
            'name': k.order.menu_item.name if k.order and k.order.menu_item else '',
            'qty': k.order.quantity if k.order else 1,
            'side': k.order.side if k.order else '',
            'time': k.completed_at.strftime('%H:%M') if k.completed_at else '',
        })
    return Response(data)
