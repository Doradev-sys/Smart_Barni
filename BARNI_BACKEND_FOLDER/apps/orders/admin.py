from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["unit_price", "line_total"]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_id", "branch", "order_type", "status", "waiter", "table", "total_amount", "order_timestamp"]
    list_filter = ["branch", "order_type", "status"]
    search_fields = ["order_id", "waiter__username", "customer__username"]
    inlines = [OrderItemInline]

admin.site.register(OrderItem)
