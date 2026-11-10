from django.contrib import admin
from django.urls import include, path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [

    path(
        "admin/",
        admin.site.urls,
    ),

    path(
        "api/auth/",
        include("apps.users.urls"),
    ),

    path(
        "api/shops/",
        include("apps.shops.urls"),
    ),

    path(
        "api/products/",
        include("apps.products.urls"),
    ),

    path(
        "api/cart/",
        include("apps.cart.urls"),
    ),

    path(
        "api/orders/",
        include("apps.orders.urls"),
    ),

    path(
        "api/delivery/",
        include("apps.delivery.urls"),
    ),

    path(
        "api/token/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),

    path(
        "api/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),

    path(
    "api/payments/",
    include("apps.payments.urls"),
),
]