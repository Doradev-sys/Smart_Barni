from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Category, MenuItem
from .serializers import CategorySerializer, MenuItemSerializer

class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.filter(is_active=True)

class MenuItemListView(generics.ListAPIView):
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        qs = MenuItem.objects.filter(is_active=True, category__is_active=True).select_related("category").prefetch_related("recipe_boms__ingredient")
        category_id = self.request.query_params.get("category_id")
        if category_id:
            qs = qs.filter(category_id=category_id)
        return qs
