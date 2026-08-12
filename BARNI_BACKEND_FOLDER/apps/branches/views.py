from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Branch, DiningTable
from .serializers import BranchSerializer, DiningTableSerializer


class BranchListView(generics.ListAPIView):
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Branch.objects.filter(is_active=True)
        if self.request.user.branch_id:
            qs = qs.filter(pk=self.request.user.branch_id)
        return qs


class AvailableTableListView(generics.ListAPIView):
    serializer_class = DiningTableSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = DiningTable.objects.filter(
            status=DiningTable.Status.FREE, branch__is_active=True
        ).select_related("branch")
        requested_branch = self.request.query_params.get("branch_id")
        if self.request.user.branch_id:
            qs = qs.filter(branch_id=self.request.user.branch_id)
        elif requested_branch:
            qs = qs.filter(branch_id=requested_branch)
        return qs
