from decimal import Decimal
from rest_framework import serializers
from apps.branches.models import Branch, DiningTable
from apps.menu.models import MenuItem
from .models import Order, OrderItem, OrderIssue

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

    def create(self, validated_data):
        from .services import OrderService
        return OrderService.create_waiter_order(
            waiter=self.context["request"].user,
            branch=validated_data["branch"],
            table=validated_data["table"],
            items=validated_data["items"],
            notes=validated_data.get("notes", ""),
        )

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

class ReportIssueSerializer(serializers.Serializer):
    issue_type = serializers.ChoiceField(choices=OrderIssue.IssueType.choices)
    description = serializers.CharField(allow_blank=False, trim_whitespace=True)

    def validate_description(self, value):
        if not value.strip():
            raise serializers.ValidationError("Description cannot be empty.")
        return value.strip()


class OrderIssueSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="pk", read_only=True)
    reported_by_name = serializers.CharField(source="reported_by.full_name", read_only=True)
    class Meta:
        model = OrderIssue
        fields = ["id", "issue_id", "order", "reported_by", "reported_by_name", "issue_type", "description", "created_at"]
        read_only_fields = fields


class OrderSummarySerializer(serializers.Serializer):
    total_sale = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_revenue = serializers.DecimalField(max_digits=14, decimal_places=2)
    order_count = serializers.IntegerField()
    date_from = serializers.DateField()
    date_to = serializers.DateField()

class OrderRowSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="pk", read_only=True)
    table_number = serializers.CharField(source="table.table_number", read_only=True, default=None)
    waiter_name = serializers.CharField(source="waiter.full_name", read_only=True, default=None)
    ui_status = serializers.SerializerMethodField()
    is_paid = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "order_id", "table_number", "waiter_name", "order_type", "ui_status", "total_amount", "order_timestamp", "is_paid"]
        read_only_fields = fields

    def get_is_paid(self, obj):
        return getattr(obj, "_is_paid_cache", None) or OrderSerializer(context=self.context).get_is_paid(obj)

    def get_ui_status(self, obj):
        return OrderSerializer(context=self.context).get_ui_status(obj)