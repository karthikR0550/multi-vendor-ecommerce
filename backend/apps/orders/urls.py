from django.urls import path

from .views import (
    AcceptShopOrderView,
    CheckoutView,
    MyOrderDetailView,
    MyOrderListView,
    PackShopOrderView,
    ShopOwnerOrderListView,
)


urlpatterns = [

    # =========================
    # CUSTOMER
    # =========================

    path(
        "checkout/",
        CheckoutView.as_view(),
        name="checkout",
    ),

    path(
        "my-orders/",
        MyOrderListView.as_view(),
        name="my-orders",
    ),

    path(
        "my-orders/<int:pk>/",
        MyOrderDetailView.as_view(),
        name="my-order-detail",
    ),


    # =========================
    # SHOP OWNER
    # =========================

    path(
        "shop/",
        ShopOwnerOrderListView.as_view(),
        name="shop-orders",
    ),

    path(
        "shop/<int:pk>/accept/",
        AcceptShopOrderView.as_view(),
        name="shop-order-accept",
    ),

    path(
        "shop/<int:pk>/pack/",
        PackShopOrderView.as_view(),
        name="shop-order-pack",
    ),
]