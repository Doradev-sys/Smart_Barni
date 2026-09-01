from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, MenuItemViewSet, menu_full_view

router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('items', MenuItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('full/', menu_full_view, name='menu-full'),
]
