from django.conf import settings
from django.db import models

from apps.orders.models import ShopOrder


class DeliveryAssignment(models.Model):

    class Status(models.TextChoices):
        ASSIGNED = "ASSIGNED", "Assigned"
        PICKED_UP = "PICKED_UP", "Picked Up"
        OUT_FOR_DELIVERY = (
            "OUT_FOR_DELIVERY",
            "Out for Delivery",
        )
        DELIVERED = "DELIVERED", "Delivered"

    shop_order = models.OneToOneField(
        ShopOrder,
        on_delete=models.CASCADE,
        related_name="delivery_assignment",
    )

    delivery_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="delivery_assignments",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.ASSIGNED,
    )

    assigned_at = models.DateTimeField(
        auto_now_add=True
    )

    picked_up_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    out_for_delivery_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            f"Delivery #{self.id} - "
            f"Shop Order #{self.shop_order_id}"
        )