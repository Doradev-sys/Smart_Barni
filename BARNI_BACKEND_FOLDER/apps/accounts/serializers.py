from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import Profile 

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'full_name', 'phone', 'profile_picture']

    def get_full_name(self, obj):
        full = f"{obj.first_name} {obj.last_name}".strip()
        return full or obj.username

    def get_phone(self, obj):
        if hasattr(obj, 'profile') and obj.profile:
            return obj.profile.phone_number or ''
        return ''

    def get_profile_picture(self, obj):
        if hasattr(obj, 'profile') and obj.profile and obj.profile.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile.profile_picture.url)
            return obj.profile.profile_picture.url
        return ''


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(required=False, default='')
    father_name = serializers.CharField(required=False, default='')
    phone = serializers.CharField(required=False, default='')

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'full_name', 'father_name', 'phone']

    def create(self, validated_data):
        full_name = validated_data.pop('full_name', '')
        father_name = validated_data.pop('father_name', '')
        phone = validated_data.pop('phone', '')
        parts = full_name.split(' ', 1)
        first_name = parts[0] if parts else ''
        last_name = parts[1] if len(parts) > 1 else ''
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data.get('role', 'Waiter'),
            first_name=first_name,
            last_name=last_name,
        )
        if phone:
            from .models import Profile
            Profile.objects.create(user=user, phone_number=phone)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid credentials")


class CustomerLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data['username']
        password = data['password']
        try:
            user = User.objects.get(username=username)
            if not user.check_password(password):
                raise serializers.ValidationError("Incorrect password.")
            if user.role != 'Customer':
                raise serializers.ValidationError("This account is not a customer account.")
            return user
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=username,
                password=password,
                role='Customer',
                first_name=username,
            )
            return user


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

# ============================================================================
# PROFILE SERIALIZERS
# ============================================================================

class ProfileSerializer(serializers.ModelSerializer):
    """Profile serializer for CRUD"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)
    
    class Meta:
        model = Profile
        fields = ['id', 'user', 'username', 'email', 'role', 'phone_number', 
                  'father_name', 'profile_picture', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Profile update serializer"""
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    
    class Meta:
        model = Profile
        fields = ['phone_number', 'father_name', 'profile_picture', 'first_name', 'last_name']
    
    def update(self, instance, validated_data):
        user = instance.user
        if 'first_name' in validated_data:
            user.first_name = validated_data.pop('first_name')
        if 'last_name' in validated_data:
            user.last_name = validated_data.pop('last_name')
        user.save()
        return super().update(instance, validated_data)


class UserProfileHistorySerializer(serializers.ModelSerializer):
    """User profile with history"""
    profile = ProfileSerializer(read_only=True)
    order_count = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()
    recent_orders = serializers.SerializerMethodField()
    login_history = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'first_name', 'last_name', 
                  'is_active', 'date_joined', 'profile', 'order_count', 
                  'total_spent', 'recent_orders', 'login_history']
    
    def get_order_count(self, obj):
        return obj.customer_orders.count()
    
    def get_total_spent(self, obj):
        from django.db.models import Sum
        from apps.orders.models import Order
        result = Order.objects.filter(customer=obj, payment_status='paid').aggregate(
            total=Sum('total')
        )
        return result['total'] or 0
    
    def get_recent_orders(self, obj):
        from apps.orders.models import Order
        from apps.orders.serializers import OrderSerializer
        orders = Order.objects.filter(customer=obj).order_by('-created_at')[:5]
        return OrderSerializer(orders, many=True).data
    
    def get_login_history(self, obj):
        from .models import LoginAuditLog
        logs = LoginAuditLog.objects.filter(user=obj).order_by('-login_time')[:10]
        return [
            {
                'login_time': log.login_time,
                'ip_address': log.ip_address
            }
            for log in logs
        ]