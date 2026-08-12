from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("log_id", "entity_type", "entity_id", "action", "user", "created_at")
    list_filter = ("action", "entity_type")
    search_fields = ("entity_type", "entity_id", "user__username")
    readonly_fields = [f.name for f in AuditLog._meta.fields]
