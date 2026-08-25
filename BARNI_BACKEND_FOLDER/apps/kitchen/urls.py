from django.urls import path
from .views import kitchen_queue_view, kitchen_queue_count_view, kitchen_history_view, update_kitchen_status_view, create_kitchen_entry_view

urlpatterns = [
    path('queue/', kitchen_queue_view, name='kitchen-queue'),
    path('queue/count/', kitchen_queue_count_view, name='kitchen-queue-count'),
    path('history/', kitchen_history_view, name='kitchen-history'),
    path('<uuid:kitchen_id>/status/', update_kitchen_status_view, name='kitchen-status'),
    path('create/<uuid:order_id>/', create_kitchen_entry_view, name='kitchen-create'),
]
