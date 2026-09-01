from django.contrib import admin
from .models import Delivery


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['order', 'driver', 'status', 'created_at']
    list_filter = ['status']
