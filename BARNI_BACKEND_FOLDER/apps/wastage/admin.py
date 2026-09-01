from django.contrib import admin
from .models import WastageRecord


@admin.register(WastageRecord)
class WastageRecordAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'quantity', 'unit', 'reason', 'cost', 'created_at']
