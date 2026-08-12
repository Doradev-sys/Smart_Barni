from decimal import Decimal
from rest_framework import serializers
from .models import Category, MenuItem


def menu_stock_state(item):
    try:
        from apps.inventory.services import _leaf_requirements
        from apps.inventory.models import Ingredient
        required = _leaf_requirements(item, Decimal("1"))
        if not required:
            return "UNAVAILABLE"
        ingredients = Ingredient.objects.filter(ingredient_id__in=required.keys())
        by_id = {x.ingredient_id: x for x in ingredients}
        if set(by_id) != set(required):
            return "UNAVAILABLE"
        if any(by_id[iid].current_stock < required[iid] for iid in required):
            return "UNAVAILABLE"
        if any(by_id[iid].current_stock <= by_id[iid].reorder_level for iid in required):
            return "LOW_STOCK"
        return "AVAILABLE"
    except Exception:
        return "UNAVAILABLE"

class CategorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="pk", read_only=True)
    class Meta:
        model = Category
        fields = ["id", "category_id", "name", "cuisine_type", "meal_period", "display_order", "is_active"]

class MenuItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="pk", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    stock_state = serializers.SerializerMethodField()
    class Meta:
        model = MenuItem
        fields = ["id", "item_id", "category", "category_name", "name", "description", "selling_price", "labor_pct", "rent_pct", "utility_pct", "kitchen_station", "is_active", "image_url", "created_at", "stock_state"]
    def get_stock_state(self, obj):
        return menu_stock_state(obj)
