from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, process_payment_view, admin_refund_order_view

router = DefaultRouter()
router.register('payments', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('process/', process_payment_view, name='process-payment'),
    
    # Refund URL
    path('admin/orders/<uuid:order_id>/refund/', admin_refund_order_view, name='admin-refund-order'),
]