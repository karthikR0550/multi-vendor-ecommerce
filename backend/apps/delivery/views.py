from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.accounting.models import VendorEarning
from apps.orders.models import Order, ShopOrder
from apps.users.models import User
from apps.users.permissions import IsAdmin, IsDelivery

from .models import DeliveryAssignment
from .serializers import DeliveryAssignmentSerializer
from rest_framework.views import APIView


# =========================================================
# ADMIN - ASSIGN DELIVERY
# =========================================================

class AssignDeliveryView(generics.GenericAPIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        shop_order_id = request.data.get(
            "shop_order"
        )

        delivery_person_id = request.data.get(
            "delivery_person"
        )

        if not shop_order_id:
            raise ValidationError(
                {
                    "shop_order":
                        "Shop order is required."
                }
            )

        if not delivery_person_id:
            raise ValidationError(
                {
                    "delivery_person":
                        "Delivery person is required."
                }
            )

        # Get ShopOrder
        try:
            shop_order = ShopOrder.objects.get(
                pk=shop_order_id
            )

        except ShopOrder.DoesNotExist:
            raise ValidationError(
                {
                    "shop_order":
                        "Shop order not found."
                }
            )

        # Only PACKED orders can be assigned
        if (
            shop_order.status
            != ShopOrder.Status.PACKED
        ):
            raise ValidationError(
                {
                    "shop_order": (
                        "Only packed orders can "
                        "be assigned for delivery."
                    )
                }
            )

        # Prevent duplicate delivery assignment
        if hasattr(
            shop_order,
            "delivery_assignment"
        ):
            raise ValidationError(
                {
                    "shop_order": (
                        "This shop order already "
                        "has a delivery assignment."
                    )
                }
            )

        # Find valid delivery person
        try:
            delivery_person = User.objects.get(
                pk=delivery_person_id,
                role=User.Role.DELIVERY,
                is_active=True,
            )

        except User.DoesNotExist:
            raise ValidationError(
                {
                    "delivery_person": (
                        "Valid active delivery "
                        "person not found."
                    )
                }
            )

        # Create delivery assignment
        assignment = (
            DeliveryAssignment.objects.create(
                shop_order=shop_order,
                delivery_person=delivery_person,
                status=(
                    DeliveryAssignment
                    .Status
                    .ASSIGNED
                ),
            )
        )

        return Response(
            {
                "message":
                    "Delivery assigned successfully.",

                "delivery_assignment":
                    DeliveryAssignmentSerializer(
                        assignment
                    ).data,
            },
            status=status.HTTP_201_CREATED,
        )


# =========================================================
# ADMIN - VIEW ALL DELIVERY ASSIGNMENTS
# =========================================================

class DeliveryAssignmentListView(
    generics.ListAPIView
):
    serializer_class = (
        DeliveryAssignmentSerializer
    )

    permission_classes = [IsAdmin]

    def get_queryset(self):
        return (
            DeliveryAssignment.objects
            .select_related(
                "delivery_person",
                "shop_order",
                "shop_order__shop",
                "shop_order__order",
            )
            .order_by("-assigned_at")
        )

# =========================================================
# ADMIN - LIST AVAILABLE DELIVERY PERSONS
# =========================================================

class DeliveryPersonListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        delivery_persons = User.objects.filter(
            role=User.Role.DELIVERY,
            is_active=True,
        ).values("id", "username")

        return Response(list(delivery_persons))
# =========================================================
# DELIVERY PERSON - VIEW MY DELIVERIES
# =========================================================
# =========================================================
# ADMIN - LIST PACKED ORDERS AVAILABLE FOR DELIVERY
# =========================================================

class PackedOrdersListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        packed_orders = (
            ShopOrder.objects
            .filter(
                status=ShopOrder.Status.PACKED
            )
            .exclude(
                delivery_assignment__isnull=False
            )
            .select_related(
                "shop",
                "order",
            )
            .values(
                "id",
                "order_id",
                "shop__name",
                "order__shipping_name",
                "subtotal",
                "status",
            )
        )

        return Response(list(packed_orders))
class MyDeliveryListView(
    generics.ListAPIView
):
    serializer_class = (
        DeliveryAssignmentSerializer
    )

    permission_classes = [IsDelivery]

    def get_queryset(self):
        return (
            DeliveryAssignment.objects
            .filter(
                delivery_person=self.request.user
            )
            .select_related(
                "delivery_person",
                "shop_order",
                "shop_order__shop",
                "shop_order__order",
            )
            .order_by("-assigned_at")
        )


# =========================================================
# DELIVERY PERSON - PICK UP ORDER
# =========================================================

class PickUpDeliveryView(
    generics.GenericAPIView
):
    permission_classes = [IsDelivery]

    def post(self, request, pk):

        try:
            assignment = (
                DeliveryAssignment.objects
                .select_related(
                    "shop_order"
                )
                .get(
                    pk=pk,
                    delivery_person=request.user,
                )
            )

        except DeliveryAssignment.DoesNotExist:
            return Response(
                {
                    "detail":
                        "Delivery assignment not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Must currently be ASSIGNED
        if (
            assignment.status
            != DeliveryAssignment.Status.ASSIGNED
        ):
            raise ValidationError(
                {
                    "status": (
                        "Only assigned deliveries "
                        "can be picked up."
                    )
                }
            )

        # Update delivery assignment
        assignment.status = (
            DeliveryAssignment.Status.PICKED_UP
        )

        assignment.picked_up_at = (
            timezone.now()
        )

        assignment.save(
            update_fields=[
                "status",
                "picked_up_at",
                "updated_at",
            ]
        )

        return Response(
            {
                "message":
                    "Order picked up successfully.",

                "delivery_assignment":
                    DeliveryAssignmentSerializer(
                        assignment
                    ).data,
            }
        )


# =========================================================
# DELIVERY PERSON - OUT FOR DELIVERY
# =========================================================

class OutForDeliveryView(
    generics.GenericAPIView
):
    permission_classes = [IsDelivery]

    def post(self, request, pk):

        try:
            assignment = (
                DeliveryAssignment.objects
                .select_related(
                    "shop_order"
                )
                .get(
                    pk=pk,
                    delivery_person=request.user,
                )
            )

        except DeliveryAssignment.DoesNotExist:
            return Response(
                {
                    "detail":
                        "Delivery assignment not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Order must first be picked up
        if (
            assignment.status
            != DeliveryAssignment.Status.PICKED_UP
        ):
            raise ValidationError(
                {
                    "status": (
                        "The order must be picked "
                        "up first."
                    )
                }
            )

        # Update delivery assignment
        assignment.status = (
            DeliveryAssignment
            .Status
            .OUT_FOR_DELIVERY
        )

        assignment.out_for_delivery_at = (
            timezone.now()
        )

        assignment.save(
            update_fields=[
                "status",
                "out_for_delivery_at",
                "updated_at",
            ]
        )

        # Current ShopOrder SHIPPED status
        # represents Out For Delivery.
        assignment.shop_order.status = (
            ShopOrder.Status.SHIPPED
        )

        assignment.shop_order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return Response(
            {
                "message":
                    "Order is out for delivery.",

                "delivery_assignment":
                    DeliveryAssignmentSerializer(
                        assignment
                    ).data,
            }
        )


# =========================================================
# DELIVERY PERSON - MARK ORDER DELIVERED
# =========================================================

class CompleteDeliveryView(
    generics.GenericAPIView
):
    permission_classes = [IsDelivery]

    def post(self, request, pk):

        try:
            assignment = (
                DeliveryAssignment.objects
                .select_related(
                    "shop_order",
                    "shop_order__order",
                )
                .get(
                    pk=pk,
                    delivery_person=request.user,
                )
            )

        except DeliveryAssignment.DoesNotExist:
            return Response(
                {
                    "detail":
                        "Delivery assignment not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Must be OUT_FOR_DELIVERY
        if (
            assignment.status
            != DeliveryAssignment
            .Status
            .OUT_FOR_DELIVERY
        ):
            raise ValidationError(
                {
                    "status": (
                        "Only orders that are out "
                        "for delivery can be "
                        "marked as delivered."
                    )
                }
            )

        # Update DeliveryAssignment
        assignment.status = (
            DeliveryAssignment.Status.DELIVERED
        )

        assignment.delivered_at = (
            timezone.now()
        )

        assignment.save(
            update_fields=[
                "status",
                "delivered_at",
                "updated_at",
            ]
        )

        # Update ShopOrder
        assignment.shop_order.status = (
            ShopOrder.Status.DELIVERED
        )

        assignment.shop_order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )
                 # Make vendor earning available after
        # successful delivery.
        try:
            vendor_earning = (
                assignment.shop_order.vendor_earning
            )

            if (
                vendor_earning.status
                == VendorEarning.Status.PENDING
            ):
                vendor_earning.status = (
                    VendorEarning.Status.AVAILABLE
                )

                vendor_earning.save(
                    update_fields=[
                        "status",
                        "updated_at",
                    ]
                )

        except VendorEarning.DoesNotExist:
            pass
        # =================================================
        # UPDATE MAIN CUSTOMER ORDER
        # =================================================

        main_order = (
            assignment.shop_order.order
        )
         
        # Check whether there are any ShopOrders
        # that have NOT been delivered.
        all_delivered = (
            not main_order.shop_orders.exclude(
                status=ShopOrder.Status.DELIVERED
            ).exists()
        )

        # If every ShopOrder is delivered,
        # complete the main Order.
        if all_delivered:

            main_order.status = (
                Order.Status.COMPLETED
            )

            main_order.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        return Response(
            {
                "message":
                    "Order delivered successfully.",

                "delivery_assignment":
                    DeliveryAssignmentSerializer(
                        assignment
                    ).data,

                "order_status":
                    main_order.status,
            }
        )