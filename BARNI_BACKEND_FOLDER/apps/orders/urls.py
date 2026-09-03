from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderViewSet, ReceiptViewSet, TableViewSet,
    place_order_view, customer_place_order_view,
    accept_order_view, cancel_order_view, pay_order_view,
    customer_orders_view, customer_order_count_view, tables_view,
    customer_create_order_view,
    customer_order_detail_view,
    customer_orders_history_view,
    customer_cancel_order_view,
    customer_pay_order_view,
    customer_payment_history_view,
    dashboard_summary_view,
    dashboard_hourly_view,
    dashboard_top_performance_view,
)

router = DefaultRouter()
router.register('orders', OrderViewSet)
router.register('receipts', ReceiptViewSet)
router.register('tables', TableViewSet)

urlpatterns = [
    # Existing URLs
    path('', include(router.urls)),
    path('place/', place_order_view, name='place-order'),
    path('customer/place/', customer_place_order_view, name='customer-place-order'),
    path('customer/my-orders/', customer_orders_view, name='customer-orders'),
    path('customer/count/', customer_order_count_view, name='customer-order-count'),
    path('<uuid:order_id>/accept/', accept_order_view, name='accept-order'),
    path('<uuid:order_id>/cancel/', cancel_order_view, name='cancel-order'),
    path('<uuid:order_id>/pay/', pay_order_view, name='pay-order'),
    path('tables/', tables_view, name='tables-list'),
    
    # Customer Order URLs
    path('customer/orders/create/', customer_create_order_view, name='customer-order-create'),
    path('customer/orders/', customer_orders_history_view, name='customer-orders-history'),
    path('customer/orders/<uuid:order_id>/', customer_order_detail_view, name='customer-order-detail'),
    path('customer/orders/<uuid:order_id>/cancel/', customer_cancel_order_view, name='customer-order-cancel'),
    
    # Payment URLs
    path('customer/orders/<uuid:order_id>/pay/', customer_pay_order_view, name='customer-order-pay'),
    path('customer/payments/', customer_payment_history_view, name='customer-payment-history'),
    
    # Dashboard URLs
    path('admin/dashboard/summary/', dashboard_summary_view, name='dashboard-summary'),
    path('admin/dashboard/hourly/', dashboard_hourly_view, name='dashboard-hourly'),
    path('admin/dashboard/top-performance/', dashboard_top_performance_view, name='dashboard-top-performance'),
]