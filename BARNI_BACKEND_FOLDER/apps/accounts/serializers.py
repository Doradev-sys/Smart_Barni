from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from .models import Role

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source="role.role_name", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "full_name",
            "phone",
            "role",
            "role_name",
            "branch",
            "branch_name",
            "is_active",
            "created_at",
            "last_login_at",
        ]
        read_only_fields = [
            "id",
            "role_name",
            "branch_name",
            "created_at",
            "last_login_at",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    """Public registration creates customers only.

    Staff roles/branches must be assigned by an authorized administrator so a
    public caller cannot register themselves as a waiter or choose a branch.
    """

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "email", "password", "full_name", "phone"]

    def create(self, validated_data):
        role, _ = Role.objects.get_or_create(role_name="CUSTOMER")
        password = validated_data.pop("password")
        return User.objects.create_user(role=role, password=password, **validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])
        if not user or not user.is_active:
            raise serializers.ValidationError("Invalid credentials")
        return user
