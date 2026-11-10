from decimal import Decimal

from django.db import transaction
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.cart.models import Cart
from apps.products.models import Product
from apps.shops.models import Shop
from apps.users.permissions import IsCustomer, IsShopOwner

from .models import Order, OrderItem, ShopOrder
from .serializers import OrderSerializer, ShopOrderSerializer


# =========================================================
# CUSTOMER - CHECKOUT
# =========================================================

class CheckoutView(generics.GenericAPIView):
    permission_classes = [IsCustomer]

    @transaction.atomic
    def post(self, request):
        try:
            cart = Cart.objects.prefetch_related(
                "items__product__shop"
            ).get(customer=request.user)

        except Cart.DoesNotExist:
            raise ValidationError(
                {"cart": "Your cart is empty."}
            )

        cart_items = list(cart.items.all())

        if not cart_items:
            raise ValidationError(
                {"cart": "Your cart is empty."}
            )

        # Validate shipping information
        required_fields = [
            "shipping_name",
            "shipping_phone",
            "shipping_address",
            "shipping_city",
            "shipping_state",
            "shipping_postal_code",
        ]

        errors = {}

        for field in required_fields:
            if not request.data.get(field):
                errors[field] = "This field is required."

        if errors:
            raise ValidationError(errors)

        # Lock and validate products
        locked_products = {}

        for cart_item in cart_items:

            try:
                product = (
                    Product.objects
                    .select_for_update()
                    .select_related("shop")
                    .get(
                        pk=cart_item.product_id,
                        status=Product.Status.APPROVED,
                        is_active=True,
                        shop__status=Shop.Status.APPROVED,
                    )
                )

            except Product.DoesNotExist:
                raise ValidationError(
                    {
                        "product": (
                            f"Product {cart_item.product.name} "
                            "is no longer available."
                        )
                    }
                )

            if cart_item.quantity > product.stock:
                raise ValidationError(
                    {
                        "stock": (
                            f"Only {product.stock} units of "
                            f"{product.name} are available."
                        )
                    }
                )

            locked_products[product.id] = product

        # Create main customer order
        order = Order.objects.create(
            customer=request.user,
            shipping_name=request.data["shipping_name"],
            shipping_phone=request.data["shipping_phone"],
            shipping_address=request.data["shipping_address"],
            shipping_city=request.data["shipping_city"],
            shipping_state=request.data["shipping_state"],
            shipping_postal_code=request.data[
                "shipping_postal_code"
            ],
            status=Order.Status.PENDING,
        )

        shop_orders = {}
        order_total = Decimal("0.00")

        # Split cart items according to shop
        for cart_item in cart_items:

            product = locked_products[
                cart_item.product_id
            ]

            # Create one ShopOrder for each shop
            if product.shop_id not in shop_orders:

                shop_orders[
                    product.shop_id
                ] = ShopOrder.objects.create(
                    order=order,
                    shop=product.shop,
                    status=ShopOrder.Status.PENDING,
                    subtotal=Decimal("0.00"),
                )

            shop_order = shop_orders[
                product.shop_id
            ]

            item_subtotal = (
                product.price * cart_item.quantity
            )

            # Create order item
            OrderItem.objects.create(
                shop_order=shop_order,
                product=product,
                product_name=product.name,
                unit_price=product.price,
                quantity=cart_item.quantity,
                subtotal=item_subtotal,
            )

            # Update shop subtotal
            shop_order.subtotal += item_subtotal

            # Update main order total
            order_total += item_subtotal

            # Reduce product stock
            product.stock -= cart_item.quantity

            product.save(
                update_fields=["stock"]
            )

        # Save each shop subtotal
        for shop_order in shop_orders.values():

            shop_order.save(
                update_fields=["subtotal"]
            )

        # Save main order total
        order.total_amount = order_total

        order.save(
            update_fields=["total_amount"]
        )

        # Clear customer's cart after successful checkout
        cart.items.all().delete()

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )


# =========================================================
# CUSTOMER - ORDER HISTORY
# =========================================================

class MyOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsCustomer]

    def get_queryset(self):

        return (
            Order.objects
            .filter(
                customer=self.request.user
            )
            .prefetch_related(
                "shop_orders__items"
            )
            .order_by("-created_at")
        )


# =========================================================
# CUSTOMER - ORDER DETAILS
# =========================================================

class MyOrderDetailView(
    generics.RetrieveAPIView
):
    serializer_class = OrderSerializer
    permission_classes = [IsCustomer]

    def get_queryset(self):

        return (
            Order.objects
            .filter(
                customer=self.request.user
            )
            .prefetch_related(
                "shop_orders__items"
            )
        )


# =========================================================
# SHOP OWNER - VIEW ORDERS
# =========================================================

class ShopOwnerOrderListView(
    generics.ListAPIView
):
    serializer_class = ShopOrderSerializer
    permission_classes = [IsShopOwner]

    def get_queryset(self):

        return (
            ShopOrder.objects
            .filter(
                shop__owner=self.request.user
            )
            .select_related(
                "order",
                "shop",
            )
            .prefetch_related(
                "items"
            )
            .order_by("-created_at")
        )


# =========================================================
# SHOP OWNER - ACCEPT ORDER
# =========================================================

class AcceptShopOrderView(
    generics.GenericAPIView
):
    permission_classes = [IsShopOwner]

    def post(self, request, pk):

        try:
            shop_order = ShopOrder.objects.get(
                pk=pk,
                shop__owner=request.user,
            )

        except ShopOrder.DoesNotExist:

            return Response(
                {
                    "detail":
                    "Shop order not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Only pending orders can be accepted
        if (
            shop_order.status
            != ShopOrder.Status.PENDING
        ):

            raise ValidationError(
                {
                    "status": (
                        "Only pending orders "
                        "can be accepted."
                    )
                }
            )

        shop_order.status = (
            ShopOrder.Status.ACCEPTED
        )

        shop_order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return Response(
            {
                "message":
                "Order accepted successfully.",

                "shop_order":
                ShopOrderSerializer(
                    shop_order
                ).data,
            }
        )


# =========================================================
# SHOP OWNER - MARK ORDER AS PACKED
# =========================================================

class PackShopOrderView(
    generics.GenericAPIView
):
    permission_classes = [IsShopOwner]

    def post(self, request, pk):

        try:
            shop_order = ShopOrder.objects.get(
                pk=pk,
                shop__owner=request.user,
            )

        except ShopOrder.DoesNotExist:

            return Response(
                {
                    "detail":
                    "Shop order not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Only accepted orders can be packed
        if (
            shop_order.status
            != ShopOrder.Status.ACCEPTED
        ):

            raise ValidationError(
                {
                    "status": (
                        "Only accepted orders "
                        "can be marked as packed."
                    )
                }
            )

        shop_order.status = (
            ShopOrder.Status.PACKED
        )

        shop_order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return Response(
            {
                "message": (
                    "Order marked as "
                    "packed and ready."
                ),

                "shop_order":
                ShopOrderSerializer(
                    shop_order
                ).data,
            }
        )