from rest_framework import serializers
from .models import KitchenOrder
from apps.orders.serializers import OrderSerializer


class KitchenOrderSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    menu_item_name = serializers.SerializerMethodField()
    menu_item_emoji = serializers.SerializerMethodField()
    menu_item_price = serializers.SerializerMethodField()
    menu_item_ingredients = serializers.SerializerMethodField()

    class Meta:
        model = KitchenOrder
        fields = '__all__'

    def get_menu_item_name(self, obj):
        return obj.order.menu_item.name if obj.order and obj.order.menu_item else ''

    def get_menu_item_emoji(self, obj):
        return obj.order.menu_item.emoji if obj.order and obj.order.menu_item else ''

    def get_menu_item_price(self, obj):
        if obj.order and obj.order.menu_item:
            return float(obj.order.menu_item.price)
        return 0

    def get_menu_item_ingredients(self, obj):
        if obj.order and obj.order.menu_item:
            return [
                {'name': i.name, 'quantity': i.quantity, 'is_raw': i.is_raw}
                for i in obj.order.menu_item.ingredients.all()
            ]
        return []


class KitchenOrderUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['preparing', 'ready', 'done'])
    notes = serializers.CharField(required=False, default='')
