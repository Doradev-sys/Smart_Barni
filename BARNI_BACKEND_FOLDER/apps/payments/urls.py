from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, process_payment_view

router = DefaultRouter()
router.register('payments', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('process/', process_payment_view, name='process-payment'),
]
