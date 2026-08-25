from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, finance_summary_view

router = DefaultRouter()
router.register('transactions', TransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('summary/', finance_summary_view, name='finance-summary'),
]
