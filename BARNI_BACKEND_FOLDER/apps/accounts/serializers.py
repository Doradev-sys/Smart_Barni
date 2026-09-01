from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from .models import CustomerAddress

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'first_name', 'last_name', 'full_name']
        read_only_fields = ['id', 'username', 'role']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class CustomerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'first_name', 'last_name']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        return User.objects.create_user(
            password=password,
            role=User.Role.CUSTOMER,
            **validated_data,
        )


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user or not user.is_active:
            raise serializers.ValidationError('Invalid credentials.')
        return user


class CustomerLoginSerializer(LoginSerializer):
    def validate(self, data):
        user = super().validate(data)
        if user.role != User.Role.CUSTOMER:
            raise serializers.ValidationError('This account is not a customer account.')
        return user


class CustomerProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

    def validate_email(self, value):
        user = self.instance
        if User.objects.filter(email__iexact=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value


class CustomerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddress
        fields = [
            'id', 'label', 'recipient_name', 'phone', 'address_line',
            'city', 'area', 'landmark', 'is_default',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.role != User.Role.CUSTOMER:
            raise serializers.ValidationError('Only customer accounts can manage customer addresses.')
        return attrs
