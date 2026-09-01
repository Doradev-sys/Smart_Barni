from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import WastageRecord
from .serializers import WastageRecordSerializer

class WastageRecordViewSet(viewsets.ModelViewSet):
    queryset = WastageRecord.objects.all()
    serializer_class = WastageRecordSerializer
    permission_classes = [IsAuthenticated]
