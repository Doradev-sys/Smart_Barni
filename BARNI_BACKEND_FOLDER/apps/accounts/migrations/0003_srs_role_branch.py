import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.utils import timezone


def seed_roles_and_migrate_users(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")
    User = apps.get_model("accounts", "User")
    Profile = apps.get_model("accounts", "Profile")
    roles = {
        "ADMIN": "Owner / Admin",
        "WAITER": "Waiter / Waitstaff",
        "KITCHEN_HEAD": "Kitchen Head",
        "KITCHEN_STAFF": "Kitchen Staff",
        "DELIVERY_DRIVER": "Delivery Driver",
        "CUSTOMER": "Customer",
        "SYSTEM_ADMIN": "System Administrator",
        "MANAGER": "Manager",
        "CASHIER": "Cashier",
    }
    for name, description in roles.items():
        Role.objects.get_or_create(role_name=name, defaults={"description": description})

    mapping = {
        "WAITSTAFF": "WAITER",
        "Waitstaff": "WAITER",
        "Cashier": "CASHIER",
        "CASHIER": "CASHIER",
        "Kitchen": "KITCHEN_STAFF",
        "Manager": "MANAGER",
        "ADMIN": "ADMIN",
        "Admin": "ADMIN",
        "WAITER": "WAITER",
        "KITCHEN": "KITCHEN_STAFF",
        "KITCHEN_STAFF": "KITCHEN_STAFF",
        "KITCHEN_HEAD": "KITCHEN_HEAD",
        "DELIVERY_DRIVER": "DELIVERY_DRIVER",
        "CUSTOMER": "CUSTOMER",
        "SYSTEM_ADMIN": "SYSTEM_ADMIN",
    }
    default_role = Role.objects.get(role_name="CUSTOMER")
    for user in User.objects.all().iterator():
        legacy = getattr(user, "legacy_role", None)
        role_name = mapping.get(legacy, str(legacy).upper() if legacy else "CUSTOMER")
        role = Role.objects.filter(role_name=role_name).first() or default_role
        user.role_id = role.pk
        if not user.full_name:
            user.full_name = " ".join(part for part in [user.first_name, user.last_name] if part).strip() or user.username
        profile = Profile.objects.filter(user_id=user.pk).first()
        if profile and profile.phone_number and not user.phone:
            user.phone = profile.phone_number
        user.save(update_fields=["role", "full_name", "phone"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_alter_loginauditlog_options_alter_user_options_and_more"),
        ("branches", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Role",
            fields=[
                ("role_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("role_name", models.CharField(max_length=50, unique=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("permissions", models.JSONField(blank=True, null=True)),
            ],
            options={"db_table": "roles", "ordering": ["role_name"]},
        ),
        migrations.RenameField(
            model_name="user",
            old_name="role",
            new_name="legacy_role",
        ),
        migrations.AddField(
            model_name="user",
            name="role",
            field=models.ForeignKey(
                blank=True,
                db_column="role_id",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="users",
                to="accounts.role",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="full_name",
            field=models.CharField(default="", max_length=120),
        ),
        migrations.AddField(
            model_name="user",
            name="phone",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="branch",
            field=models.ForeignKey(
                blank=True,
                db_column="branch_id",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="users",
                to="branches.branch",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="pin_code",
            field=models.CharField(blank=True, help_text="Optional hashed POS PIN/RFID token; never store plaintext.", max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="created_at",
            field=models.DateTimeField(default=timezone.now, editable=False),
        ),
        migrations.RunPython(seed_roles_and_migrate_users, noop_reverse),
        migrations.AlterField(
            model_name="user",
            name="id",
            field=models.BigAutoField(db_column="user_id", primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.ForeignKey(
                db_column="role_id",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="users",
                to="accounts.role",
            ),
        ),
        migrations.RemoveField(model_name="user", name="legacy_role"),
        migrations.AlterModelOptions(
            name="user",
            options={"ordering": ["-created_at"]},
        ),
        migrations.AlterModelTable(name="user", table="users"),
    ]
