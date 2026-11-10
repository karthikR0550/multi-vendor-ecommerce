from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.users.permissions import IsAdmin

from .models import Shop
from .serializers import ShopSerializer


class ShopApplicationView(generics.CreateAPIView):
    serializer_class = ShopSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user

        if hasattr(user, "shop"):
            raise ValidationError(
                "You have already submitted a shop application."
            )

        user.role = "SHOP_OWNER"
        user.save(update_fields=["role"])

        serializer.save(
            owner=user,
            status=Shop.Status.PENDING,
        )


class MyShopView(generics.RetrieveAPIView):
    serializer_class = ShopSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            return self.request.user.shop
        except Shop.DoesNotExist:
            raise ValidationError(
                "You do not have a shop."
            )


class PendingShopListView(generics.ListAPIView):
    serializer_class = ShopSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return Shop.objects.filter(
            status=Shop.Status.PENDING
        ).order_by("created_at")


class ApproveShopView(generics.GenericAPIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            shop = Shop.objects.get(pk=pk)
        except Shop.DoesNotExist:
            return Response(
                {"detail": "Shop not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        shop.status = Shop.Status.APPROVED
        shop.rejection_reason = ""
        shop.save(
            update_fields=[
                "status",
                "rejection_reason",
                "updated_at",
            ]
        )

        return Response(
            {
                "message": "Shop approved successfully.",
                "shop": ShopSerializer(shop).data,
            }
        )


class RejectShopView(generics.GenericAPIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            shop = Shop.objects.get(pk=pk)
        except Shop.DoesNotExist:
            return Response(
                {"detail": "Shop not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        reason = request.data.get(
            "reason",
            "Shop application rejected."
        )

        shop.status = Shop.Status.REJECTED
        shop.rejection_reason = reason
        shop.save(
            update_fields=[
                "status",
                "rejection_reason",
                "updated_at",
            ]
        )

        return Response(
            {
                "message": "Shop rejected successfully.",
                "shop": ShopSerializer(shop).data,
            }
        )