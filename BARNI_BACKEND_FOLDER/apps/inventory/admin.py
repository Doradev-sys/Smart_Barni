from django.contrib import admin
from .models import Ingredient, RecipeBOM, StockTransaction, Supplier
for model in [Ingredient, RecipeBOM, StockTransaction, Supplier]:
    admin.site.register(model)