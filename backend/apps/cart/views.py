from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.products.models import Product
from apps.shops.models import Shop
from apps.users.permissions import IsCustomer

from .models import Cart, CartItem
from .serializers import CartSerializer


class CartView(generics.GenericAPIView):
    permission_classes = [IsCustomer]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(
            customer=request.user
        )

        return Response(
            CartSerializer(cart).data
        )


class AddToCartView(generics.GenericAPIView):
    permission_classes = [IsCustomer]

    def post(self, request):
        product_id = request.data.get("product")
        quantity = request.data.get("quantity", 1)

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            raise ValidationError(
                {"quantity": "Quantity must be a number."}
            )

        if quantity < 1:
            raise ValidationError(
                {"quantity": "Quantity must be at least 1."}
            )

        try:
            product = Product.objects.get(
                id=product_id,
                status=Product.Status.APPROVED,
                is_active=True,
                shop__status=Shop.Status.APPROVED,
            )
        except Product.DoesNotExist:
            raise ValidationError(
                {"product": "Product is not available."}
            )

        cart, created = Cart.objects.get_or_create(
            customer=request.user
        )

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity},
        )

        if not created:
            new_quantity = cart_item.quantity + quantity

            if new_quantity > product.stock:
                raise ValidationError(
                    {"quantity": "Requested quantity exceeds available stock."}
                )

            cart_item.quantity = new_quantity
            cart_item.save(update_fields=["quantity"])

        elif quantity > product.stock:
            cart_item.delete()

            raise ValidationError(
                {"quantity": "Requested quantity exceeds available stock."}
            )

        return Response(
            CartSerializer(cart).data,
            status=status.HTTP_200_OK,
        )


class UpdateCartItemView(generics.GenericAPIView):
    permission_classes = [IsCustomer]

    def patch(self, request, pk):
        try:
            cart_item = CartItem.objects.get(
                pk=pk,
                cart__customer=request.user,
            )
        except CartItem.DoesNotExist:
            return Response(
                {"detail": "Cart item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        quantity = request.data.get("quantity")

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            raise ValidationError(
                {"quantity": "Valid quantity is required."}
            )

        if quantity < 1:
            raise ValidationError(
                {"quantity": "Quantity must be at least 1."}
            )

        if quantity > cart_item.product.stock:
            raise ValidationError(
                {"quantity": "Requested quantity exceeds available stock."}
            )

        cart_item.quantity = quantity
        cart_item.save(update_fields=["quantity"])

        return Response(
            CartSerializer(cart_item.cart).data
        )


class RemoveCartItemView(generics.GenericAPIView):
    permission_classes = [IsCustomer]

    def delete(self, request, pk):
        try:
            cart_item = CartItem.objects.get(
                pk=pk,
                cart__customer=request.user,
            )
        except CartItem.DoesNotExist:
            return Response(
                {"detail": "Cart item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        cart = cart_item.cart
        cart_item.delete()

        return Response(
            CartSerializer(cart).data
        )