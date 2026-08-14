from decimal import Decimal
from rest_framework import serializers
from apps.branches.models import Branch, DiningTable
from apps.menu.models import MenuItem
from .models import Order, OrderItem

class OrderItemInputSerializer(serializers.Serializer):
    menu_item_id = serializers.IntegerField(min_value=1)
    quantity = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=Decimal("0.01"))
    notes = serializers.CharField(required=False, allow_blank=True)

class CreateWaiterOrderSerializer(serializers.Serializer):
    branch_id = serializers.IntegerField(min_value=1)
    table_id = serializers.IntegerField(min_value=1)
    items = OrderItemInputSerializer(many=True, allow_empty=False)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        branch = Branch.objects.filter(pk=attrs["branch_id"], is_active=True).first()
        if not branch:
            raise serializers.ValidationError({"branch_id": "Active branch not found."})
        user = self.context["request"].user
        if user.branch_id and user.branch_id != branch.pk:
            raise serializers.ValidationError({"branch_id": "Waiter is assigned to a different branch."})
        table = DiningTable.objects.filter(pk=attrs["table_id"], branch=branch).first()
        if not table:
            raise serializers.ValidationError({"table_id": "Table does not belong to this branch."})
        if table.status not in {DiningTable.Status.FREE}:
            raise serializers.ValidationError({"table_id": "Selected table is not free."})
        menu_ids = [x["menu_item_id"] for x in attrs["items"]]
        items = MenuItem.objects.filter(pk__in=menu_ids, is_active=True, category__is_active=True)
        found = set(items.values_list("pk", flat=True))
        missing = sorted(set(menu_ids) - found)
        if missing:
            raise serializers.ValidationError({"items": f"Unavailable/unknown menu item IDs: {missing}"})
        attrs["branch"] = branch
        attrs["table"] = table
        return attrs

class OrderItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="pk", read_only=True)
    menu_item_name = serializers.CharField(source="item.name", read_only=True)
    class Meta:
        model = OrderItem
        fields = ["id", "order_item_id", "item", "menu_item_name", "quantity", "unit_price", "line_total", "prep_status", "kitchen_station", "notes", "sent_to_kitchen_at", "ready_at"]

class OrderSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="pk", read_only=True)
    waiter_name = serializers.CharField(source="waiter.full_name", read_only=True)
    table_number = serializers.CharField(source="table.table_number", read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    ui_status = serializers.SerializerMethodField()
    ui_order_type = serializers.SerializerMethodField()
    is_paid = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ["id", "order_id", "branch", "table", "table_number", "waiter", "waiter_name", "customer", "order_timestamp", "status", "ui_status", "order_type", "ui_order_type", "subtotal", "tax_amount", "total_amount", "payment_method", "notes", "closed_at", "is_paid", "items"]
        read_only_fields = fields

    def get_is_paid(self, obj):
        from django.db.models import Sum
        from decimal import Decimal
        paid = obj.payments.filter(status="SUCCESS").aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        return paid >= obj.total_amount

    def get_ui_status(self, obj):
        if obj.status == Order.Status.CANCELLED:
            return "CANCELLED"
        if obj.status == Order.Status.CLOSED:
            return "COMPLETED"
        if obj.order_type == Order.OrderType.DELIVERY:
            if obj.status == Order.Status.READY:
                return "ONLINE"
            if obj.status == Order.Status.SERVED:
                return "SERVED"
        if self.get_is_paid(obj):
            return "PAID"
        if obj.status == Order.Status.SENT:
            return "ORDERED"
        return obj.status

    def get_ui_order_type(self, obj):
        if obj.order_type == Order.OrderType.DELIVERY and obj.customer_id:
            return "ONLINE"
        return "WAITER" if obj.order_type == Order.OrderType.DINE_IN else obj.order_type
