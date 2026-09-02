# apps/orders/serializers.py
# ============================================================================
# COMPLETE SERIALIZERS FILE
# ============================================================================

from rest_framework import serializers
from .models import Order, Receipt, Table, OrderItem
from apps.menu.serializers import MenuItemLightSerializer


# ============================================================================
# NEW SERIALIZERS FOR CUSTOMER ORDERS
# ============================================================================

class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model"""
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    menu_item_emoji = serializers.CharField(source='menu_item.emoji', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'menu_item_name', 'menu_item_emoji', 
                  'quantity', 'price', 'subtotal', 'notes', 'created_at']


class CustomerOrderCreateSerializer(serializers.Serializer):
    """Serializer for customer creating order with multiple items"""
    items = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        help_text="List of menu items with quantities"
    )
    order_type = serializers.ChoiceField(
        choices=[('dine_in', 'Dine In'), ('delivery', 'Delivery')], 
        default='dine_in'
    )
    delivery_address = serializers.CharField(required=False, allow_blank=True, default='')
    table_number = serializers.IntegerField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True, default='')
    payment_method = serializers.ChoiceField(
        choices=Order.PAYMENT_CHOICES, 
        required=False, 
        default=''
    )
    
    def validate_items(self, items):
        """Validate each item exists and is available"""
        if not items:
            raise serializers.ValidationError("At least one item is required")
        
        for item in items:
            if 'menu_item_id' not in item:
                raise serializers.ValidationError("Each item must have menu_item_id")
            if 'quantity' not in item or item['quantity'] < 1:
                raise serializers.ValidationError("Each item must have quantity >= 1")
            
            from apps.menu.models import MenuItem
            try:
                menu_item = MenuItem.objects.get(id=item['menu_item_id'])
                if not menu_item.is_available:
                    raise serializers.ValidationError(f"{menu_item.name} is not available")
            except MenuItem.DoesNotExist:
                raise serializers.ValidationError(f"Menu item {item['menu_item_id']} not found")
        return items
    
    def validate(self, data):
        """Validate delivery address for delivery orders"""
        if data.get('order_type') == 'delivery' and not data.get('delivery_address'):
            raise serializers.ValidationError({
                'delivery_address': "Delivery address is required for delivery orders"
            })
        return data


class CustomerOrderSerializer(serializers.ModelSerializer):
    """Serializer for customer viewing orders"""
    items = OrderItemSerializer(many=True, read_only=True)
    table_number = serializers.IntegerField(source='table.number', read_only=True, default=None)
    customer_name = serializers.CharField(source='customer.username', read_only=True, default='')
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'customer', 'customer_name', 'items',
            'subtotal', 'tax', 'delivery_fee', 'total',
            'status', 'payment_method', 'payment_status', 'order_type',
            'delivery_address', 'table_number', 'notes',
            'created_at', 'updated_at', 'estimated_delivery_time'
        ]


# ============================================================================
# EXISTING SERIALIZERS (UPDATED)
# ============================================================================

class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model"""
    items = OrderItemSerializer(many=True, read_only=True)
    
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True, default='')
    menu_item_emoji = serializers.CharField(source='menu_item.emoji', read_only=True, default='')
    menu_item_price = serializers.DecimalField(source='menu_item.price', max_digits=10, decimal_places=2, read_only=True, default=0)
    table_number = serializers.IntegerField(source='table.number', read_only=True, default=None)
    customer_name = serializers.CharField(source='customer.username', read_only=True, default='')
    waiter_name = serializers.CharField(source='waiter.username', read_only=True, default='')

    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'menu_item', 'menu_item_name', 'menu_item_emoji',
            'menu_item_price', 'table', 'table_number', 'customer', 'customer_name',
            'waiter', 'waiter_name', 'side', 'quantity', 'subtotal', 'tax',
            'delivery_fee', 'total', 'status', 'source', 'payment_method',
            'payment_status', 'qr_data', 'notes', 'created_at', 'updated_at', 
            'order_type', 'delivery_address', 'estimated_delivery_time', 'items'
        ]


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating a single-item order"""
    menu_item_id = serializers.UUIDField()
    table_id = serializers.IntegerField(required=False, allow_null=True)
    side = serializers.CharField(max_length=50, default='Plain')
    quantity = serializers.IntegerField(min_value=1, default=1)
    source = serializers.ChoiceField(choices=Order.SOURCE_CHOICES, default='barni')
    payment_method = serializers.ChoiceField(choices=Order.PAYMENT_CHOICES, required=False, default='')
    qr_data = serializers.CharField(required=False, default='')
    notes = serializers.CharField(required=False, default='')


class ReceiptSerializer(serializers.ModelSerializer):
    """Serializer for Receipt model"""
    class Meta:
        model = Receipt
        fields = '__all__'


class TableSerializer(serializers.ModelSerializer):
    """Serializer for Table model"""
    class Meta:
        model = Table
        fields = ['id', 'number', 'is_active']