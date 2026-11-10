from rest_framework import serializers

from .models import Shop


class ShopSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(
        source="owner.username",
        read_only=True
    )

    class Meta:
        model = Shop
        fields = [
            "id",
            "owner",
            "name",
            "description",
            "phone",
            "email",
            "address",
            "city",
            "state",
            "postal_code",
            "status",
            "rejection_reason",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "owner",
            "status",
            "rejection_reason",
            "created_at",
            "updated_at",
        ]