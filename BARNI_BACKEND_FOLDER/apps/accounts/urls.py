from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    customer_register_view,
    customer_login_view,
    customer_profile_view,
    CustomerAddressListCreateView,
    CustomerAddressDetailView,
)

urlpatterns = [
    path('customer/register/', customer_register_view, name='customer-register'),
    path('customer/login/', customer_login_view, name='customer-login'),
    path('customer/me/', customer_profile_view, name='customer-profile'),
    path('customer/addresses/', CustomerAddressListCreateView.as_view(), name='customer-address-list'),
    path('customer/addresses/<int:pk>/', CustomerAddressDetailView.as_view(), name='customer-address-detail'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
