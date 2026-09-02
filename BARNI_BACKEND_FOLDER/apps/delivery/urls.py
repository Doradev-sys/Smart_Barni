from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DeliveryViewSet,
    customer_track_delivery_view,
    customer_delivery_history_view,
    driver_deliveries_view,
    update_delivery_status_view,
)

router = DefaultRouter()
router.register('deliveries', DeliveryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # Customer Delivery Tracking URLs
    path('customer/track/<uuid:order_id>/', customer_track_delivery_view, name='customer-track-delivery'),
    path('customer/history/', customer_delivery_history_view, name='customer-delivery-history'),
    
    # Driver URLs
    path('driver/assigned/', driver_deliveries_view, name='driver-deliveries'),
    path('driver/update/<uuid:delivery_id>/', update_delivery_status_view, name='update-delivery-status'),
]