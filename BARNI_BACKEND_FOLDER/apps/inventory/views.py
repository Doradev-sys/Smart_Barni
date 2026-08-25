from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import InventoryItem
from .serializers import InventoryItemSerializer


class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticated]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def low_stock_view(request):
    items = InventoryItem.objects.filter(is_active=True)
    low = [item for item in items if item.is_low_stock]
    return Response(InventoryItemSerializer(low, many=True).data)
