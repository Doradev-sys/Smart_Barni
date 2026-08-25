from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderViewSet, ReceiptViewSet, TableViewSet,
    place_order_view, customer_place_order_view,
    accept_order_view, cancel_order_view, pay_order_view,
    customer_orders_view, customer_order_count_view, tables_view,
)

router = DefaultRouter()
router.register('orders', OrderViewSet)
router.register('receipts', ReceiptViewSet)
router.register('tables', TableViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('place/', place_order_view, name='place-order'),
    path('customer/place/', customer_place_order_view, name='customer-place-order'),
    path('customer/my-orders/', customer_orders_view, name='customer-orders'),
    path('customer/count/', customer_order_count_view, name='customer-order-count'),
    path('<uuid:order_id>/accept/', accept_order_view, name='accept-order'),
    path('<uuid:order_id>/cancel/', cancel_order_view, name='cancel-order'),
    path('<uuid:order_id>/pay/', pay_order_view, name='pay-order'),
    path('tables/', tables_view, name='tables-list'),
]
