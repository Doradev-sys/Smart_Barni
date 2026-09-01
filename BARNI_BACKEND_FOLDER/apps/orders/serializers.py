from rest_framework import serializers
from .models import Order, Receipt, Table
from apps.menu.serializers import MenuItemLightSerializer


class OrderSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True, default='')
    menu_item_emoji = serializers.CharField(source='menu_item.emoji', read_only=True, default='')
    menu_item_price = serializers.DecimalField(source='menu_item.price', max_digits=10, decimal_places=2, read_only=True, default=0)
    table_number = serializers.IntegerField(source='table.number', read_only=True, default=None)
    customer_name = serializers.CharField(source='customer.username', read_only=True, default='')
    waiter_name = serializers.CharField(source='waiter.username', read_only=True, default='')

    class Meta:
        model = Order
        fields = '__all__'


class OrderCreateSerializer(serializers.Serializer):
    menu_item_id = serializers.UUIDField()
    table_id = serializers.IntegerField(required=False, allow_null=True)
    side = serializers.CharField(max_length=50, default='Plain')
    quantity = serializers.IntegerField(min_value=1, default=1)
    source = serializers.ChoiceField(choices=Order.SOURCE_CHOICES, default='barni')
    payment_method = serializers.ChoiceField(choices=Order.PAYMENT_CHOICES, required=False, default='')
    qr_data = serializers.CharField(required=False, default='')
    notes = serializers.CharField(required=False, default='')


class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = '__all__'


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ['id', 'number', 'is_active']
