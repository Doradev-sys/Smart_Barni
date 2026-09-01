from django.contrib import admin
from .models import InventoryItem


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'quantity', 'unit', 'min_threshold']
    list_filter = ['category', 'is_active']
