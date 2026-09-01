from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InventoryItemViewSet, low_stock_view

router = DefaultRouter()
router.register('items', InventoryItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('low-stock/', low_stock_view, name='low-stock'),
]
