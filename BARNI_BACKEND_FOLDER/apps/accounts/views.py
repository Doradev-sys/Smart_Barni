from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomerAddress, User
from .permissions import IsCustomer
from .serializers import (
    CustomerAddressSerializer,
    CustomerLoginSerializer,
    CustomerProfileUpdateSerializer,
    CustomerRegisterSerializer,
    UserSerializer,
)


def token_response(user, request, http_status=status.HTTP_200_OK):
    refresh = RefreshToken.for_user(user)
    return Response({
        'user': UserSerializer(user, context={'request': request}).data,
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }, status=http_status)


@api_view(['POST'])
@permission_classes([AllowAny])
def customer_register_view(request):
    serializer = CustomerRegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return token_response(user, request, status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def customer_login_view(request):
    serializer = CustomerLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return token_response(serializer.validated_data, request)


@api_view(['GET', 'PATCH', 'PUT'])
@permission_classes([IsAuthenticated, IsCustomer])
def customer_profile_view(request):
    if request.method == 'GET':
        return Response(UserSerializer(request.user, context={'request': request}).data)

    serializer = CustomerProfileUpdateSerializer(
        request.user,
        data=request.data,
        partial=request.method == 'PATCH',
    )
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response(UserSerializer(user, context={'request': request}).data)


class CustomerAddressListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = CustomerAddressSerializer

    def get_queryset(self):
        return CustomerAddress.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):
        if serializer.validated_data.get('is_default'):
            CustomerAddress.objects.filter(customer=self.request.user, is_default=True).update(is_default=False)
        serializer.save(customer=self.request.user)


class CustomerAddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = CustomerAddressSerializer

    def get_queryset(self):
        return CustomerAddress.objects.filter(customer=self.request.user)

    def perform_update(self, serializer):
        if serializer.validated_data.get('is_default'):
            CustomerAddress.objects.filter(customer=self.request.user, is_default=True).exclude(pk=serializer.instance.pk).update(is_default=False)
        serializer.save()
