from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import register_view, login_view, current_user_view, logout_view, upload_profile_picture_view

urlpatterns = [
    path('register/', register_view, name='api-register'),
    path('login/', login_view, name='api-login'),
    path('logout/', logout_view, name='api-logout'),
    path('me/', current_user_view, name='api-current-user'),
    path('upload-picture/', upload_profile_picture_view, name='api-upload-picture'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]