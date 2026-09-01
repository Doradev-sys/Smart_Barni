from django.contrib import admin
from .models import Category, MenuItem, Ingredient

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'sort_order', 'is_active']

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'item_type', 'category', 'is_available']
    list_filter = ['item_type', 'category', 'is_available']

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity', 'menu_item', 'is_raw']
