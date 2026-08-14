from rest_framework import serializers
from .models import Branch, DiningTable

class BranchSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="pk", read_only=True)
    class Meta:
        model = Branch
        fields = ["id", "branch_id", "name", "address", "phone", "is_active"]
        read_only_fields = ["branch_id"]

class DiningTableSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="pk", read_only=True)
    class Meta:
        model = DiningTable
        fields = ["id", "table_id", "branch", "table_number", "capacity", "status", "location"]
        read_only_fields = ["table_id"]
