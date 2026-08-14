from django.urls import path
from .views import current_user_view, login_view, register_view

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("me/", current_user_view, name="current-user"),
]
