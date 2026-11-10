from django.db import models

from apps.orders.models import ShopOrder
from apps.shops.models import Shop


class VendorEarning(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        AVAILABLE = "AVAILABLE", "Available"
        SETTLED = "SETTLED", "Settled"
        REVERSED = "REVERSED", "Reversed"

    shop = models.ForeignKey(
        Shop,
        on_delete=models.PROTECT,
        related_name="earnings",
    )

    shop_order = models.OneToOneField(
        ShopOrder,
        on_delete=models.PROTECT,
        related_name="vendor_earning",
    )
    settlement = models.ForeignKey(
        "Settlement",
        on_delete=models.PROTECT,
        related_name="earnings",
        null=True,
        blank=True,
    )
    gross_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    commission_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    vendor_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return (
            f"Earning #{self.id} - "
            f"{self.shop.name} - "
            f"{self.vendor_amount}"
        )

class Settlement(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    shop = models.ForeignKey(
        Shop,
        on_delete=models.PROTECT,
        related_name="settlements",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    reference_number = models.CharField(
        max_length=100,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    failure_reason = models.TextField(
        blank=True,
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return (
            f"Settlement #{self.id} - "
            f"{self.shop.name} - "
            f"{self.amount}"
        )