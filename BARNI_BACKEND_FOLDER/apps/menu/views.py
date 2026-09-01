from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.views.decorators.cache import cache_page
from .models import Category, MenuItem
from .serializers import CategorySerializer, MenuItemSerializer, MenuItemLightSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.prefetch_related('items').all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.select_related('category').prefetch_related('ingredients').all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return MenuItemLightSerializer
        return MenuItemSerializer


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@cache_page(60)
def menu_full_view(request):
    categories = Category.objects.prefetch_related('items__ingredients').filter(is_active=True)
    return Response(CategorySerializer(categories, many=True).data)
