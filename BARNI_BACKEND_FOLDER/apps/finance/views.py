from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum
from .models import Transaction
from .serializers import TransactionSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def finance_summary_view(request):
    income = Transaction.objects.filter(transaction_type='income').aggregate(total=Sum('amount'))['total'] or 0
    expense = Transaction.objects.filter(transaction_type='expense').aggregate(total=Sum('amount'))['total'] or 0
    return Response({'income': income, 'expense': expense, 'profit': income - expense})
