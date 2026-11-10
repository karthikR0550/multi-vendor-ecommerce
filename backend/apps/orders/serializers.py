
from rest_framework import serializers

from .models import Order, OrderItem, ShopOrder


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "unit_price",
            "quantity",
            "subtotal",
        ]


class ShopOrderSerializer(serializers.ModelSerializer):

    shop_name = serializers.CharField(
        source="shop.name",
        read_only=True,
    )

    order_id = serializers.IntegerField(
        source="order.id",
        read_only=True,
    )

    customer_name = serializers.CharField(
        source="order.shipping_name",
        read_only=True,
    )

    customer_phone = serializers.CharField(
        source="order.shipping_phone",
        read_only=True,
    )

    shipping_address = serializers.CharField(
        source="order.shipping_address",
        read_only=True,
    )

    shipping_city = serializers.CharField(
        source="order.shipping_city",
        read_only=True,
    )

    shipping_state = serializers.CharField(
        source="order.shipping_state",
        read_only=True,
    )

    shipping_postal_code = serializers.CharField(
        source="order.shipping_postal_code",
        read_only=True,
    )

    items = OrderItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = ShopOrder
        fields = [
            "id",
            "order_id",
            "shop",
            "shop_name",
            "customer_name",
            "customer_phone",
            "shipping_address",
            "shipping_city",
            "shipping_state",
            "shipping_postal_code",
            "status",
            "subtotal",
            "items",
            "created_at",
        ]


class OrderSerializer(serializers.ModelSerializer):

    shop_orders = ShopOrderSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "total_amount",
            "shipping_name",
            "shipping_phone",
            "shipping_address",
            "shipping_city",
            "shipping_state",
            "shipping_postal_code",
            "shop_orders",
            "created_at",
            "updated_at",
        ]
