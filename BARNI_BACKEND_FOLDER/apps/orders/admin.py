from django.contrib import admin
from .models import Order, Receipt, Table

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'menu_item', 'table', 'status', 'source', 'payment_method', 'created_at']
    list_filter = ['status', 'source', 'payment_method']

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'total', 'payment_method', 'created_at']

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['number', 'is_active']
