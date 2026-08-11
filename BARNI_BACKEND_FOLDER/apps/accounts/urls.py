from django.urls import path
from .views import register_view, login_view, current_user_view

urlpatterns = [
    path('register/', register_view, name='api-register'),
    path('login/', login_view, name='api-login'),
    path('me/', current_user_view, name='api-current-user'),
]