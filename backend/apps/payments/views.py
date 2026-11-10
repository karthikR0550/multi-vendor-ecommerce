from decimal import Decimal

import hashlib
import hmac
import json
import razorpay
from django.conf import settings
from django.db import models
from django.db import transaction
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.accounting.models import VendorEarning
from apps.cart.models import Cart
from apps.orders.models import Order, OrderItem, ShopOrder
from apps.products.models import Product
from apps.shops.models import Shop
from apps.users.permissions import IsCustomer

from .models import Payment, Refund, WebhookEvent
from .services import get_razorpay_client

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny

class CreateRazorpayOrderView(generics.GenericAPIView):
    permission_classes = [IsCustomer]

    def post(self, request):
        try:
            cart = (
                Cart.objects
                .prefetch_related(
                    "items__product__shop"
                )
                .get(customer=request.user)
            )

        except Cart.DoesNotExist:
            raise ValidationError(
                {"cart": "Your cart is empty."}
            )

        cart_items = list(cart.items.all())

        if not cart_items:
            raise ValidationError(
                {"cart": "Your cart is empty."}
            )

        total_amount = Decimal("0.00")

        for cart_item in cart_items:
            product = cart_item.product

            if (
                product.status
                != Product.Status.APPROVED
                or not product.is_active
                or product.shop.status
                != Shop.Status.APPROVED
            ):
                raise ValidationError(
                    {
                        "product": (
                            f"{product.name} is "
                            "not currently available."
                        )
                    }
                )

            if cart_item.quantity > product.stock:
                raise ValidationError(
                    {
                        "stock": (
                            f"Only {product.stock} units "
                            f"of {product.name} are available."
                        )
                    }
                )

            total_amount += (
                product.price
                * cart_item.quantity
            )

        if total_amount <= 0:
            raise ValidationError(
                {"amount": "Invalid payment amount."}
            )

        amount_in_paise = int(
            total_amount * 100
        )

        try:
            client = get_razorpay_client()

            razorpay_order = client.order.create(
                {
                    "amount": amount_in_paise,
                    "currency": "INR",
                    "payment_capture": 1,
                    "notes": {
                        "customer_id": str(
                            request.user.id
                        ),
                        "username": (
                            request.user.username
                        ),
                    },
                }
            )

        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
            )

        except razorpay.errors.BadRequestError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception:
            return Response(
                {
                    "detail": (
                        "Unable to create Razorpay "
                        "order at this time."
                    )
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        payment = Payment.objects.create(
            customer=request.user,
            amount=total_amount,
            status=Payment.Status.PENDING,
            payment_method="RAZORPAY",
            razorpay_order_id=(
                razorpay_order["id"]
            ),
        )

        return Response(
            {
                "payment_id": payment.id,
                "razorpay_order_id": (
                    razorpay_order["id"]
                ),
                "amount": razorpay_order["amount"],
                "amount_rupees": str(total_amount),
                "currency": razorpay_order["currency"],
                "key_id": settings.RAZORPAY_KEY_ID,
                "payment_status": payment.status,
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyRazorpayPaymentView(
    generics.GenericAPIView
):
    permission_classes = [IsCustomer]

    def post(self, request):
        razorpay_order_id = request.data.get(
            "razorpay_order_id"
        )

        razorpay_payment_id = request.data.get(
            "razorpay_payment_id"
        )

        razorpay_signature = request.data.get(
            "razorpay_signature"
        )

        shipping_name = request.data.get(
            "shipping_name"
        )

        shipping_phone = request.data.get(
            "shipping_phone"
        )

        shipping_address = request.data.get(
            "shipping_address"
        )

        shipping_city = request.data.get(
            "shipping_city"
        )

        shipping_state = request.data.get(
            "shipping_state"
        )

        shipping_postal_code = request.data.get(
            "shipping_postal_code"
        )

        if not all([
            razorpay_order_id,
            razorpay_payment_id,
            razorpay_signature,
        ]):
            return Response(
                {
                    "detail": (
                        "Razorpay payment information "
                        "is incomplete."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not all([
            shipping_name,
            shipping_phone,
            shipping_address,
            shipping_city,
            shipping_state,
            shipping_postal_code,
        ]):
            return Response(
                {
                    "detail": (
                        "All shipping fields are required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payment = Payment.objects.get(
                razorpay_order_id=razorpay_order_id,
                customer=request.user,
            )

        except Payment.DoesNotExist:
            return Response(
                {
                    "detail": "Payment record not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Prevent the same payment from
        # creating multiple orders.
        if (
            payment.status == Payment.Status.PAID
            and payment.order_id
        ):
            return Response(
                {
                    "detail": (
                        "Payment has already been "
                        "processed."
                    ),
                    "payment_id": payment.id,
                    "order_id": payment.order_id,
                    "payment_status": payment.status,
                },
                status=status.HTTP_200_OK,
            )

        # Verify the Razorpay signature.
        try:
            client = get_razorpay_client()

            client.utility.verify_payment_signature(
                {
                    "razorpay_order_id":
                        razorpay_order_id,

                    "razorpay_payment_id":
                        razorpay_payment_id,

                    "razorpay_signature":
                        razorpay_signature,
                }
            )

        except (
            razorpay.errors.SignatureVerificationError
        ):
            payment.status = Payment.Status.FAILED

            payment.failure_reason = (
                "Razorpay signature verification failed."
            )

            payment.save(
                update_fields=[
                    "status",
                    "failure_reason",
                    "updated_at",
                ]
            )

            return Response(
                {
                    "detail": (
                        "Payment verification failed."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
            )

        try:
            with transaction.atomic():

                # Lock the payment record.
                payment = (
                    Payment.objects
                    .select_for_update()
                    .get(
                        id=payment.id,
                        customer=request.user,
                    )
                )

                # Second idempotency check after
                # acquiring the database lock.
                if (
                    payment.status
                    == Payment.Status.PAID
                    and payment.order_id
                ):
                    return Response(
                        {
                            "detail": (
                                "Payment has already "
                                "been processed."
                            ),
                            "payment_id": payment.id,
                            "order_id": payment.order_id,
                            "payment_status": (
                                payment.status
                            ),
                        },
                        status=status.HTTP_200_OK,
                    )

                try:
                    cart = Cart.objects.get(
                        customer=request.user
                    )

                except Cart.DoesNotExist:
                    raise ValidationError(
                        {
                            "cart": (
                                "Cart no longer exists."
                            )
                        }
                    )

                cart_items = list(
                    cart.items.select_related(
                        "product",
                        "product__shop",
                    ).all()
                )

                if not cart_items:
                    raise ValidationError(
                        {
                            "cart": "Cart is empty."
                        }
                    )

                locked_products = {}

                # Lock all products involved in
                # this purchase.
                for cart_item in cart_items:
                    product = (
                        Product.objects
                        .select_for_update()
                        .select_related("shop")
                        .get(
                            id=cart_item.product_id
                        )
                    )

                    locked_products[
                        product.id
                    ] = product

                calculated_total = Decimal("0.00")

                # Revalidate the cart immediately
                # before creating the order.
                for cart_item in cart_items:
                    product = locked_products[
                        cart_item.product_id
                    ]

                    if (
                        product.status
                        != Product.Status.APPROVED
                        or not product.is_active
                        or product.shop.status
                        != Shop.Status.APPROVED
                    ):
                        raise ValidationError(
                            {
                                "product": (
                                    f"{product.name} is "
                                    "no longer available."
                                )
                            }
                        )

                    if (
                        cart_item.quantity
                        > product.stock
                    ):
                        raise ValidationError(
                            {
                                "stock": (
                                    f"Only {product.stock} "
                                    f"units of "
                                    f"{product.name} "
                                    "are available."
                                )
                            }
                        )

                    calculated_total += (
                        product.price
                        * cart_item.quantity
                    )

                # Never allow a changed cart total
                # to be finalized against the old
                # Razorpay payment.
                if calculated_total != payment.amount:
                    raise ValidationError(
                        {
                            "amount": (
                                "Cart total has changed "
                                "since payment was started."
                            )
                        }
                    )

                # Create the parent order.
                order = Order.objects.create(
                    customer=request.user,
                    status=Order.Status.CONFIRMED,
                    total_amount=calculated_total,
                    shipping_name=shipping_name,
                    shipping_phone=shipping_phone,
                    shipping_address=shipping_address,
                    shipping_city=shipping_city,
                    shipping_state=shipping_state,
                    shipping_postal_code=(
                        shipping_postal_code
                    ),
                )

                shop_orders = {}

                for cart_item in cart_items:
                    product = locked_products[
                        cart_item.product_id
                    ]

                    shop = product.shop

                    # Create one ShopOrder per vendor.
                    if shop.id not in shop_orders:
                        shop_order = (
                            ShopOrder.objects.create(
                                order=order,
                                shop=shop,
                                status=(
                                    ShopOrder.Status.PENDING
                                ),
                                subtotal=Decimal("0.00"),
                            )
                        )

                        shop_orders[
                            shop.id
                        ] = shop_order

                    shop_order = shop_orders[
                        shop.id
                    ]

                    item_subtotal = (
                        product.price
                        * cart_item.quantity
                    )

                    OrderItem.objects.create(
                        shop_order=shop_order,
                        product=product,
                        product_name=product.name,
                        unit_price=product.price,
                        quantity=cart_item.quantity,
                        subtotal=item_subtotal,
                    )

                    shop_order.subtotal += (
                        item_subtotal
                    )

                    # Reduce stock only after the
                    # Razorpay signature is valid.
                    product.stock -= (
                        cart_item.quantity
                    )

                    product.save(
                        update_fields=[
                            "stock",
                            "updated_at",
                        ]
                    )

                               # Save vendor subtotals.
                # Create vendor accounting records.
                commission_rate = (
                    settings.PLATFORM_COMMISSION_RATE
                )

                for shop_order in shop_orders.values():
                    shop_order.save(
                        update_fields=[
                            "subtotal",
                            "updated_at",
                        ]
                    )

                    commission_amount = (
                        shop_order.subtotal
                        * commission_rate
                        / Decimal("100")
                    ).quantize(Decimal("0.01"))

                    vendor_amount = (
                        shop_order.subtotal
                        - commission_amount
                    )

                    VendorEarning.objects.create(
                        shop=shop_order.shop,
                        shop_order=shop_order,
                        gross_amount=shop_order.subtotal,
                        commission_rate=commission_rate,
                        commission_amount=commission_amount,
                        vendor_amount=vendor_amount,
                        status=VendorEarning.Status.PENDING,
                    )

# Link payment to the new order
                # and mark it as paid.
                payment.order = order
                payment.status = Payment.Status.PAID

                payment.razorpay_payment_id = (
                    razorpay_payment_id
                )

                payment.razorpay_signature = (
                    razorpay_signature
                )

                payment.failure_reason = ""
                payment.paid_at = timezone.now()

                payment.save(
                    update_fields=[
                        "order",
                        "status",
                        "razorpay_payment_id",
                        "razorpay_signature",
                        "failure_reason",
                        "paid_at",
                        "updated_at",
                    ]
                )

                # Clear cart only after every other
                # operation succeeds.
                cart.items.all().delete()

        except ValidationError as exc:
            return Response(
                exc.detail,
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception:
            return Response(
                {
                    "detail": (
                        "Payment was verified, but "
                        "order finalization failed."
                    )
                },
                status=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
            )

        return Response(
            {
                "detail": (
                    "Payment verified and order "
                    "created successfully."
                ),
                "payment_id": payment.id,
                "payment_status": payment.status,
                "order_id": order.id,
                "order_status": order.status,
                "total_amount": str(
                    order.total_amount
                ),
            },
            status=status.HTTP_201_CREATED,
        )

class CancelOrderAndRefundView(
    generics.GenericAPIView
):
    permission_classes = [IsCustomer]

    def post(self, request, order_id):
        reason = request.data.get(
            "reason",
            "Cancelled by customer.",
        )

        try:
            order = (
                Order.objects
                .prefetch_related(
                    "shop_orders__items__product"
                )
                .get(
                    id=order_id,
                    customer=request.user,
                )
            )

        except Order.DoesNotExist:
            return Response(
                {
                    "detail": "Order not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Already cancelled.
        if order.status == Order.Status.CANCELLED:
            return Response(
                {
                    "detail": (
                        "This order is already cancelled."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Completed orders cannot be cancelled.
        if order.status == Order.Status.COMPLETED:
            return Response(
                {
                    "detail": (
                        "Completed orders cannot "
                        "be cancelled."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Do not allow cancellation once shipping
        # has started.
        non_cancellable_statuses = [
            ShopOrder.Status.SHIPPED,
            ShopOrder.Status.DELIVERED,
        ]

        if order.shop_orders.filter(
            status__in=non_cancellable_statuses
        ).exists():
            return Response(
                {
                    "detail": (
                        "This order can no longer "
                        "be cancelled because shipping "
                        "has already started."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payment = Payment.objects.get(
                order=order,
                customer=request.user,
            )

        except Payment.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "Payment record not found "
                        "for this order."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if payment.status != Payment.Status.PAID:
            return Response(
                {
                    "detail": (
                        "Only paid orders can "
                        "be refunded."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not payment.razorpay_payment_id:
            return Response(
                {
                    "detail": (
                        "Razorpay payment ID "
                        "is missing."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Prevent duplicate refunds.
        existing_refund = (
            Refund.objects
            .filter(
                payment=payment,
                status__in=[
                    Refund.Status.PENDING,
                    Refund.Status.PROCESSING,
                    Refund.Status.REFUNDED,
                ],
            )
            .first()
        )

        if existing_refund:
            return Response(
                {
                    "detail": (
                        "A refund already exists "
                        "for this payment."
                    ),
                    "refund_id": existing_refund.id,
                    "refund_status": (
                        existing_refund.status
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        refund = Refund.objects.create(
            payment=payment,
            order=order,
            customer=request.user,
            amount=payment.amount,
            reason=reason,
            status=Refund.Status.PROCESSING,
        )

        try:
            client = get_razorpay_client()

            amount_in_paise = int(
                payment.amount * 100
            )

            razorpay_refund = client.payment.refund(
                payment.razorpay_payment_id,
                {
                    "amount": amount_in_paise,
                    "notes": {
                        "order_id": str(order.id),
                        "customer_id": str(
                            request.user.id
                        ),
                        "reason": reason,
                    },
                },
            )

        except Exception as exc:
            print("RAZORPAY REFUND ERROR:", repr(exc))

            refund.status = Refund.Status.FAILED
            refund.failure_reason = repr(exc)
            refund.save(
                update_fields=[
                    "status",
                    "failure_reason",
                    "updated_at",
                ]
            )

            return Response(
                {
                    "detail": (
                        "Razorpay refund request failed."
                    ),
                    "refund_id": refund.id,
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        try:
            with transaction.atomic():

                order = (
                    Order.objects
                    .select_for_update()
                    .get(
                        id=order.id,
                        customer=request.user,
                    )
                )

                payment = (
                    Payment.objects
                    .select_for_update()
                    .get(id=payment.id)
                )

                refund = (
                    Refund.objects
                    .select_for_update()
                    .get(id=refund.id)
                )

                shop_orders = (
                    ShopOrder.objects
                    .select_for_update()
                    .filter(order=order)
                    .prefetch_related(
                        "items__product"
                    )
                )

                # Restore stock.
                for shop_order in shop_orders:
                    for item in shop_order.items.all():
                        product = (
                            Product.objects
                            .select_for_update()
                            .get(id=item.product_id)
                        )

                        product.stock += item.quantity

                        product.save(
                            update_fields=[
                                "stock",
                                "updated_at",
                            ]
                        )

                    shop_order.status = (
                        ShopOrder.Status.CANCELLED
                    )

                    shop_order.save(
                        update_fields=[
                            "status",
                            "updated_at",
                        ]
                    )

                order.status = Order.Status.CANCELLED

                order.save(
                    update_fields=[
                        "status",
                        "updated_at",
                    ]
                )

                payment.status = (
                    Payment.Status.REFUNDED
                )

                payment.save(
                    update_fields=[
                        "status",
                        "updated_at",
                    ]
                )

                refund.status = (
                    Refund.Status.REFUNDED
                )

                refund.razorpay_refund_id = (
                    razorpay_refund["id"]
                )

                refund.failure_reason = ""
                refund.refunded_at = timezone.now()

                refund.save(
                    update_fields=[
                        "status",
                        "razorpay_refund_id",
                        "failure_reason",
                        "refunded_at",
                        "updated_at",
                    ]
                )

        except Exception:
            return Response(
                {
                    "detail": (
                        "Refund was requested from "
                        "Razorpay, but local order "
                        "cancellation failed."
                    ),
                    "refund_id": refund.id,
                },
                status=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
            )

        return Response(
            {
                "detail": (
                    "Order cancelled and refund "
                    "processed successfully."
                ),
                "order_id": order.id,
                "order_status": order.status,
                "payment_status": payment.status,
                "refund_id": refund.id,
                "refund_status": refund.status,
                "razorpay_refund_id": (
                    refund.razorpay_refund_id
                ),
                "refund_amount": str(
                    refund.amount
                ),
            },
            status=status.HTTP_200_OK,
        )

@method_decorator(csrf_exempt, name="dispatch")
class RazorpayWebhookView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET

        if not webhook_secret:
            return Response(
                {
                    "detail": (
                        "Webhook secret is not configured."
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        signature = request.headers.get(
            "X-Razorpay-Signature"
        )

        event_id = request.headers.get(
            "X-Razorpay-Event-Id"
        )

        if not signature:
            return Response(
                {
                    "detail": (
                        "Razorpay signature is missing."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not event_id:
            return Response(
                {
                    "detail": (
                        "Razorpay event ID is missing."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # IMPORTANT:
        # Verify the ORIGINAL raw request body.
        raw_body = request.body

        expected_signature = hmac.new(
            webhook_secret.encode("utf-8"),
            raw_body,
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(
            expected_signature,
            signature,
        ):
            return Response(
                {
                    "detail": (
                        "Invalid webhook signature."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payload = json.loads(
                raw_body.decode("utf-8")
            )

        except (
            json.JSONDecodeError,
            UnicodeDecodeError,
        ):
            return Response(
                {
                    "detail": (
                        "Invalid webhook payload."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        event_type = payload.get("event")

        if not event_type:
            return Response(
                {
                    "detail": (
                        "Webhook event type is missing."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Razorpay can send the same event more
        # than once. Do not process it twice.
        existing_event = (
            WebhookEvent.objects
            .filter(event_id=event_id)
            .first()
        )

        if existing_event:
            return Response(
                {
                    "detail": (
                        "Webhook event already received."
                    ),
                    "event_id": event_id,
                },
                status=status.HTTP_200_OK,
            )

        webhook_event = WebhookEvent.objects.create(
            event_id=event_id,
            event_type=event_type,
            payload=payload,
            status=WebhookEvent.Status.RECEIVED,
        )

        try:
            with transaction.atomic():

                # -------------------------
                # PAYMENT CAPTURED
                # -------------------------

                if event_type == "payment.captured":
                    payment_entity = (
                        payload
                        .get("payload", {})
                        .get("payment", {})
                        .get("entity", {})
                    )

                    razorpay_payment_id = (
                        payment_entity.get("id")
                    )

                    razorpay_order_id = (
                        payment_entity.get("order_id")
                    )

                    if razorpay_order_id:
                        payment = (
                            Payment.objects
                            .select_for_update()
                            .filter(
                                razorpay_order_id=(
                                    razorpay_order_id
                                )
                            )
                            .first()
                        )

                        if payment:
                            if razorpay_payment_id:
                                payment.razorpay_payment_id = (
                                    razorpay_payment_id
                                )

                            # Do NOT mark our local
                            # Payment PAID here unless
                            # a local Order already exists.
                            #
                            # Our normal /verify/ endpoint
                            # creates the Order and performs
                            # stock/cart finalisation.
                            if payment.order_id:
                                payment.status = (
                                    Payment.Status.PAID
                                )

                                payment.paid_at = (
                                    payment.paid_at
                                    or timezone.now()
                                )

                                payment.save(
                                    update_fields=[
                                        "status",
                                        "razorpay_payment_id",
                                        "paid_at",
                                        "updated_at",
                                    ]
                                )

                            elif razorpay_payment_id:
                                payment.save(
                                    update_fields=[
                                        "razorpay_payment_id",
                                        "updated_at",
                                    ]
                                )

                # -------------------------
                # PAYMENT FAILED
                # -------------------------

                elif event_type == "payment.failed":
                    payment_entity = (
                        payload
                        .get("payload", {})
                        .get("payment", {})
                        .get("entity", {})
                    )

                    razorpay_order_id = (
                        payment_entity.get("order_id")
                    )

                    error_description = (
                        payment_entity.get(
                            "error_description"
                        )
                        or "Razorpay payment failed."
                    )

                    if razorpay_order_id:
                        payment = (
                            Payment.objects
                            .select_for_update()
                            .filter(
                                razorpay_order_id=(
                                    razorpay_order_id
                                )
                            )
                            .first()
                        )

                        if (
                            payment
                            and payment.status
                            != Payment.Status.PAID
                        ):
                            payment.status = (
                                Payment.Status.FAILED
                            )

                            payment.failure_reason = (
                                error_description
                            )

                            payment.save(
                                update_fields=[
                                    "status",
                                    "failure_reason",
                                    "updated_at",
                                ]
                            )

                # -------------------------
                # REFUND EVENTS
                # -------------------------

                elif event_type in [
                    "refund.created",
                    "refund.processed",
                    "refund.failed",
                ]:
                    refund_entity = (
                        payload
                        .get("payload", {})
                        .get("refund", {})
                        .get("entity", {})
                    )

                    razorpay_refund_id = (
                        refund_entity.get("id")
                    )

                    razorpay_payment_id = (
                        refund_entity.get(
                            "payment_id"
                        )
                    )

                    if (
                        razorpay_refund_id
                        and razorpay_payment_id
                    ):
                        payment = (
                            Payment.objects
                            .filter(
                                razorpay_payment_id=(
                                    razorpay_payment_id
                                )
                            )
                            .first()
                        )

                        if payment:
                            refund = (
                                Refund.objects
                                .filter(
                                    payment=payment,
                                    razorpay_refund_id=(
                                        razorpay_refund_id
                                    ),
                                )
                                .first()
                            )

                            if refund:
                                if (
                                    event_type
                                    == "refund.created"
                                ):
                                    refund.status = (
                                        Refund.Status.PROCESSING
                                    )

                                    refund.save(
                                        update_fields=[
                                            "status",
                                            "updated_at",
                                        ]
                                    )

                                elif (
                                    event_type
                                    == "refund.processed"
                                ):
                                    refund.status = (
                                        Refund.Status.REFUNDED
                                    )

                                    refund.failure_reason = ""
                                    refund.refunded_at = (
                                        timezone.now()
                                    )

                                    refund.save(
                                        update_fields=[
                                            "status",
                                            "failure_reason",
                                            "refunded_at",
                                            "updated_at",
                                        ]
                                    )

                                elif (
                                    event_type
                                    == "refund.failed"
                                ):
                                    refund.status = (
                                        Refund.Status.FAILED
                                    )

                                    refund.failure_reason = (
                                        refund_entity.get(
                                            "error_description"
                                        )
                                        or (
                                            "Razorpay refund "
                                            "failed."
                                        )
                                    )

                                    refund.save(
                                        update_fields=[
                                            "status",
                                            "failure_reason",
                                            "updated_at",
                                        ]
                                    )

                webhook_event.status = (
                    WebhookEvent.Status.PROCESSED
                )

                webhook_event.processed_at = (
                    timezone.now()
                )

                webhook_event.failure_reason = ""

                webhook_event.save(
                    update_fields=[
                        "status",
                        "processed_at",
                        "failure_reason",
                    ]
                )

        except Exception as exc:
            webhook_event.status = (
                WebhookEvent.Status.FAILED
            )

            webhook_event.failure_reason = str(exc)

            webhook_event.save(
                update_fields=[
                    "status",
                    "failure_reason",
                ]
            )

            return Response(
                {
                    "detail": (
                        "Webhook processing failed."
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "detail": "Webhook processed.",
                "event_id": event_id,
                "event_type": event_type,
            },
            status=status.HTTP_200_OK,
        )