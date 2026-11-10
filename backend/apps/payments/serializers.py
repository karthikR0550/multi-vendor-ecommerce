from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    order_status = serializers.CharField(
        source="order.status",
        read_only=True,
    )

    customer_username = serializers.CharField(
        source="customer.username",
        read_only=True,
    )

    class Meta:
        model = Payment

        fields = [
            "id",
            "order",
            "order_status",
            "customer",
            "customer_username",
            "amount",
            "status",
            "payment_method",
            "razorpay_order_id",
            "razorpay_payment_id",
            "failure_reason",
            "paid_at",
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields