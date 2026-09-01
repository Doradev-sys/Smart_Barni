from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Alert
from .serializers import AlertSerializer


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.select_related('author').all()
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        mine = self.request.query_params.get('mine')
        if mine:
            qs = qs.filter(author=self.request.user)
        return qs


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def respond_alert_view(request, alert_id):
    try:
        alert = Alert.objects.get(id=alert_id)
    except Alert.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    alert.response = request.data.get('response', '')
    alert.assigned_to = request.user
    alert.status = 'responded'
    alert.save()
    return Response(AlertSerializer(alert).data)
