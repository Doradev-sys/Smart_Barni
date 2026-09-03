from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    register_view, login_view, current_user_view, logout_view, 
    upload_profile_picture_view,
    profile_detail_view,          # NEW
    profile_history_view,         # NEW
    admin_user_profile_view,      # NEW
    admin_update_user_view        # NEW
)

urlpatterns = [
    # Existing URLs
    path('register/', register_view, name='api-register'),
    path('login/', login_view, name='api-login'),
    path('logout/', logout_view, name='api-logout'),
    path('me/', current_user_view, name='api-current-user'),
    path('upload-picture/', upload_profile_picture_view, name='api-upload-picture'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # NEW Profile URLs
    path('profile/', profile_detail_view, name='api-profile'),
    path('profile/history/', profile_history_view, name='api-profile-history'),
    path('admin/profile/<int:user_id>/', admin_user_profile_view, name='api-admin-profile'),
    path('admin/profile/<int:user_id>/update/', admin_update_user_view, name='api-admin-profile-update'),
]