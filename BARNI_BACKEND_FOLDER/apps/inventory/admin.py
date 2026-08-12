from django.contrib import admin
from .models import Alert, Ingredient, RecipeBOM, StockTransaction, Supplier
for model in [Alert, Ingredient, RecipeBOM, StockTransaction, Supplier]:
    admin.site.register(model)
