from decimal import Decimal
from rest_framework import serializers
from .models import Payment, PaymentProof


class PayOrderSerializer(serializers.Serializer):
    method = serializers.ChoiceField(choices=[
        ("CASH", "Cash"), ("CARD", "Card"), ("TELEBIRR", "Telebirr"),
        ("CBE_BIRR", "CBE Birr"), ("CBE", "CBE (UI alias)"), ("BOA", "BOA"),
        ("OTHER", "Other")
    ])
    gateway_ref = serializers.CharField(max_length=100, required=False, allow_blank=True)
    amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False, min_value=Decimal("0.01")
    )
    proof_image = serializers.ImageField(required=False, allow_null=True, write_only=True)

    def validate_proof_image(self, value):
        if value is not None and value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Payment proof image must be 5 MB or smaller.")
        return value

    def validate_method(self, value):
        return "CBE_BIRR" if value == "CBE" else value

    def validate(self, attrs):
        digital_methods = {"CBE_BIRR", "TELEBIRR", "BOA"}
        if attrs.get("method") in digital_methods and not attrs.get("proof_image"):
            raise serializers.ValidationError({
                "proof_image": "A screenshot/payment proof is required for digital payments."
            })
        if attrs.get("method") not in digital_methods and attrs.get("proof_image"):
            raise serializers.ValidationError({
                "proof_image": "Payment screenshots are only required for digital/transfer payments."
            })
        return attrs


class PaymentProofSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="payment_proof_id", read_only=True)
    payment_id = serializers.IntegerField(source="payment.payment_id", read_only=True)
    order_id = serializers.IntegerField(source="payment.order_id", read_only=True)
    submitted_by_name = serializers.CharField(source="submitted_by.full_name", read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.full_name", read_only=True)

    class Meta:
        model = PaymentProof
        fields = [
            "id", "payment_id", "order_id", "image", "submitted_by", "submitted_by_name",
            "submitted_at", "verification_status", "reviewed_by", "reviewed_by_name",
            "reviewed_at", "review_note"
        ]
        read_only_fields = [
            "id", "payment_id", "order_id", "submitted_by", "submitted_at",
            "verification_status", "reviewed_by", "reviewed_at"
        ]


class PaymentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="payment_id", read_only=True)
    proof = PaymentProofSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id", "payment_id", "order", "amount", "method", "gateway_ref", "status",
            "paid_at", "proof"
        ]
        read_only_fields = ["payment_id", "status", "paid_at", "proof"]
