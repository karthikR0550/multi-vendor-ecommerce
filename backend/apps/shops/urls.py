from django.urls import path

from .views import (
    ApproveShopView,
    MyShopView,
    PendingShopListView,
    RejectShopView,
    ShopApplicationView,
)

urlpatterns = [
    path(
        "apply/",
        ShopApplicationView.as_view(),
        name="shop-apply",
    ),
    path(
        "my-shop/",
        MyShopView.as_view(),
        name="my-shop",
    ),

    # Admin endpoints
    path(
        "admin/pending/",
        PendingShopListView.as_view(),
        name="pending-shops",
    ),
    path(
        "admin/<int:pk>/approve/",
        ApproveShopView.as_view(),
        name="approve-shop",
    ),
    path(
        "admin/<int:pk>/reject/",
        RejectShopView.as_view(),
        name="reject-shop",
    ),
]