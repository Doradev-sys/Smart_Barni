from django.db import models


class AuditLog(models.Model):
    log_id = models.BigAutoField(primary_key=True)
    entity_type = models.CharField(max_length=40)
    entity_id = models.BigIntegerField(blank=True, null=True)
    action = models.CharField(max_length=30)
    old_values = models.JSONField(blank=True, null=True)
    new_values = models.JSONField(blank=True, null=True)
    user = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="audit_logs", db_column="user_id", blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_log"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["entity_type", "entity_id", "created_at"], name="audit_entity_idx")]

    def __str__(self):
        return f"{self.action} {self.entity_type}#{self.entity_id}"
