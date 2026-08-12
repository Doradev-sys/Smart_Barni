from django.contrib import admin

from .models import LoginAuditLog, Profile, Role, User

admin.site.register(Role)
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(LoginAuditLog)
