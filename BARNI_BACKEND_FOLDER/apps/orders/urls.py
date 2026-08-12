from django.urls import path
from .views import OrderListCreateView, cancel_order_view, complete_order_view, receipt_view, serve_order_view
urlpatterns = [
    path("", OrderListCreateView.as_view(), name="order-list-create"),
    path("<int:pk>/cancel/", cancel_order_view, name="order-cancel"),
    path("<int:pk>/serve/", serve_order_view, name="order-serve"),
    path("<int:pk>/complete/", complete_order_view, name="order-complete"),
    path("<int:pk>/receipt/", receipt_view, name="order-receipt"),
]
