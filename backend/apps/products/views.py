from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from apps.shops.models import Shop
from apps.users.permissions import IsAdmin, IsShopOwner

from .models import Product
from .serializers import ProductSerializer


class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsShopOwner]

    def perform_create(self, serializer):
        user = self.request.user

        try:
            shop = user.shop
        except Shop.DoesNotExist:
            raise ValidationError(
                "You do not have a shop."
            )

        if shop.status != Shop.Status.APPROVED:
            raise PermissionDenied(
                "Your shop must be approved before adding products."
            )

        serializer.save(
            shop=shop,
            status=Product.Status.PENDING,
        )


class MyProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsShopOwner]

    def get_queryset(self):
        try:
            shop = self.request.user.shop
        except Shop.DoesNotExist:
            return Product.objects.none()

        return Product.objects.filter(
            shop=shop
        ).order_by("-created_at")


class MyProductManageView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsShopOwner]

    def get_queryset(self):
        try:
            shop = self.request.user.shop
        except Shop.DoesNotExist:
            return Product.objects.none()

        return Product.objects.filter(shop=shop)



class PendingProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return Product.objects.filter(
            status=Product.Status.PENDING
        ).order_by("created_at")


class ApproveProductView(generics.GenericAPIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        product.status = Product.Status.APPROVED
        product.rejection_reason = ""
        product.save(
            update_fields=[
                "status",
                "rejection_reason",
                "updated_at",
            ]
        )

        return Response(
            {
                "message": "Product approved successfully.",
                "product": ProductSerializer(product).data,
            }
        )


class RejectProductView(generics.GenericAPIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        reason = request.data.get(
            "reason",
            "Product rejected by admin."
        )

        product.status = Product.Status.REJECTED
        product.rejection_reason = reason

        product.save(
            update_fields=[
                "status",
                "rejection_reason",
                "updated_at",
            ]
        )

        return Response(
            {
                "message": "Product rejected successfully.",
                "product": ProductSerializer(product).data,
            }
        )

class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = []

    def get_queryset(self):
        queryset = Product.objects.filter(
            status=Product.Status.APPROVED,
            is_active=True,
            shop__status=Shop.Status.APPROVED,
        ).order_by("-created_at")

        search = self.request.query_params.get("search")
        category = self.request.query_params.get("category")

        if search:
            queryset = queryset.filter(
                name__icontains=search
            )

        if category:
            queryset = queryset.filter(
                category__iexact=category
            )

        return queryset


class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    permission_classes = []

    def get_queryset(self):
        return Product.objects.filter(
            status=Product.Status.APPROVED,
            is_active=True,
            shop__status=Shop.Status.APPROVED,
        )