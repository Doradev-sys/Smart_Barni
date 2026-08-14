from .models import AuditLog

def record(*, entity_type, entity_id, action, old_values=None, new_values=None, user=None, ip_address=None):
    return AuditLog.objects.create(
        entity_type=entity_type, entity_id=entity_id, action=action,
        old_values=old_values, new_values=new_values, user=user, ip_address=ip_address
    )
