from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    shop = serializers.CharField(
        source="shop.name",
        read_only=True,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "shop",
            "name",
            "description",
            "category",
            "price",
            "stock",
            "status",
            "rejection_reason",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "shop",
            "status",
            "rejection_reason",
            "created_at",
            "updated_at",
        ]