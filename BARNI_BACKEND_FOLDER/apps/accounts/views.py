from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from .serializers import (RegisterSerializer, LoginSerializer, CustomerLoginSerializer, UserSerializer, LogoutSerializer, ProfileSerializer, ProfileUpdateSerializer, UserProfileHistorySerializer
)
from .permissions import IsCustomer, IsAdmin

User = get_user_model()
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    role = request.data.get('role', '')
    if role == 'customer':
        serializer = CustomerLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    serializer = LogoutSerializer(data=request.data)
    if serializer.is_valid():
        try:
            refresh = RefreshToken(serializer.validated_data['refresh'])
            refresh.blacklist()
        except Exception:
            pass
    return Response({"ok": True}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    serializer = UserSerializer(request.user, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_profile_picture_view(request):
    if 'profile_picture' not in request.FILES:
        return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
    pic = request.FILES['profile_picture']
    if pic.size > 5 * 1024 * 1024:
        return Response({'error': 'Image too large (max 5MB)'}, status=status.HTTP_400_BAD_REQUEST)
    from .models import Profile
    profile, _ = Profile.objects.get_or_create(user=request.user)
    profile.profile_picture = pic
    profile.save()
    serializer = UserSerializer(request.user, context={'request': request})
    return Response(serializer.data)

# ============================================================================
# PROFILE VIEWS
# ============================================================================

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile_detail_view(request):
    """
    Get or update current user's profile
    GET /api/auth/profile/
    PATCH /api/auth/profile/
    """
    profile = request.user.profile
    
    if request.method == 'GET':
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
    
    # PATCH - Update profile
    serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(ProfileSerializer(profile).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_history_view(request):
    """
    Get profile with full history (orders, payments, logins)
    GET /api/auth/profile/history/
    """
    user = request.user
    serializer = UserProfileHistorySerializer(user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_user_profile_view(request, user_id):
    """
    Admin view any user's profile with history
    GET /api/auth/admin/profile/{user_id}/
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'detail': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = UserProfileHistorySerializer(user)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_update_user_view(request, user_id):
    """
    Admin update user profile
    PATCH /api/auth/admin/profile/{user_id}/update/
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'detail': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Update user fields
    if 'role' in request.data:
        user.role = request.data['role']
    if 'is_active' in request.data:
        user.is_active = request.data['is_active']
    user.save()
    
    # Update profile fields
    profile = user.profile
    if 'phone_number' in request.data:
        profile.phone_number = request.data['phone_number']
    if 'father_name' in request.data:
        profile.father_name = request.data['father_name']
    profile.save()
    
    serializer = UserProfileHistorySerializer(user)
    return Response(serializer.data)