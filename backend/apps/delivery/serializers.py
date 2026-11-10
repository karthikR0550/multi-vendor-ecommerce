
from rest_framework import serializers

from .models import DeliveryAssignment


class DeliveryAssignmentSerializer(serializers.ModelSerializer):

    delivery_person_username = serializers.CharField(
        source="delivery_person.username",
        read_only=True,
    )

    shop_name = serializers.CharField(
        source="shop_order.shop.name",
        read_only=True,
    )

    order_id = serializers.IntegerField(
        source="shop_order.order.id",
        read_only=True,
    )

    customer_name = serializers.CharField(
        source="shop_order.order.shipping_name",
        read_only=True,
    )

    customer_phone = serializers.CharField(
        source="shop_order.order.shipping_phone",
        read_only=True,
    )

    shipping_address = serializers.CharField(
        source="shop_order.order.shipping_address",
        read_only=True,
    )

    shipping_city = serializers.CharField(
        source="shop_order.order.shipping_city",
        read_only=True,
    )

    shipping_state = serializers.CharField(
        source="shop_order.order.shipping_state",
        read_only=True,
    )

    shipping_postal_code = serializers.CharField(
        source="shop_order.order.shipping_postal_code",
        read_only=True,
    )

    items = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryAssignment

        fields = [
            "id",
            "shop_order",
            "order_id",
            "shop_name",
            "delivery_person",
            "delivery_person_username",
            "customer_name",
            "customer_phone",
            "shipping_address",
            "shipping_city",
            "shipping_state",
            "shipping_postal_code",
            "items",
            "status",
            "assigned_at",
            "picked_up_at",
            "out_for_delivery_at",
            "delivered_at",
            "updated_at",
        ]

        read_only_fields = fields

    def get_items(self, obj):
        return [
            {
                "product_name": item.product_name,
                "quantity": item.quantity,
                "unit_price": str(item.unit_price),
                "subtotal": str(item.subtotal),
            }
            for item in obj.shop_order.items.all()
        ]
