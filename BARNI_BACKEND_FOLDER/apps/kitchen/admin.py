from django.contrib import admin
from .models import KitchenOrder

@admin.register(KitchenOrder)
class KitchenOrderAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'assigned_to', 'created_at']
    list_filter = ['status']
