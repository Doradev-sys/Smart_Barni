from django.urls import path
from .views import AvailableTableListView, BranchListView
urlpatterns = [
    path("", BranchListView.as_view(), name="branch-list"),
    path("tables/available/", AvailableTableListView.as_view(), name="available-tables"),
]
