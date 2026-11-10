from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "shop",
        "category",
        "price",
        "stock",
        "status",
        "created_at",
    )

    list_filter = ("status", "category")
    search_fields = ("name", "shop__name")