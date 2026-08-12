from django.urls import path
from .views import CategoryListView, MenuItemListView
urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("items/", MenuItemListView.as_view(), name="menu-item-list"),
]
