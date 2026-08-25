from rest_framework import serializers
from .models import Category, MenuItem, Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'quantity', 'is_raw']


class MenuItemSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'emoji', 'price', 'item_type', 'description', 'is_available', 'category', 'category_name', 'ingredients']


class MenuItemLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'emoji', 'price', 'item_type', 'is_available']


class CategorySerializer(serializers.ModelSerializer):
    items = MenuItemLightSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'sort_order', 'is_active', 'items']
