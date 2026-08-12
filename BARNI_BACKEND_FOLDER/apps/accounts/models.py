from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class Role(models.Model):
    role_id = models.BigAutoField(primary_key=True)
    role_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    permissions = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = "roles"
        ordering = ["role_name"]

    def __str__(self):
        return self.role_name


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, email=None, password=None, role=None, **extra_fields):
        if not username:
            raise ValueError("username is required")
        user = self.model(
            username=username,
            email=self.normalize_email(email or ""),
            **extra_fields,
        )
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        if role:
            if isinstance(role, Role):
                user.role = role
            else:
                role_obj, _ = Role.objects.get_or_create(role_name=str(role).upper())
                user.role = role_obj
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        role, _ = Role.objects.get_or_create(role_name="SYSTEM_ADMIN")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(username, email, password, role=role, **extra_fields)


class User(AbstractUser):
    """Django authentication model extended to match the DB-SRS staff/customer data.

    The repository already uses Django's BigAutoField user PK, so this integration
    preserves that PK instead of performing a destructive UUID/int migration.
    """

    id = models.BigAutoField(primary_key=True, db_column="user_id")
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="users",
        db_column="role_id",
        null=False,
    )
    full_name = models.CharField(max_length=120, blank=False, default="")
    phone = models.CharField(max_length=20, blank=True, null=True)
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="users",
        db_column="branch_id",
        blank=True,
        null=True,
    )
    pin_code = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Optional hashed POS PIN/RFID token; never store plaintext.",
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    objects = UserManager()

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.username} ({self.role.role_name})"

    @property
    def role_name(self):
        return self.role.role_name


class Profile(models.Model):
    # Preserved from the repository's existing accounts module.
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Profile for {self.user.username}"


class LoginAuditLog(models.Model):
    # Preserved from the repository's existing accounts module.
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} logged in at {self.login_time}"
