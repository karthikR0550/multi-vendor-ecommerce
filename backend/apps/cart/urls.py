from django.urls import path

from .views import (
    AddToCartView,
    CartView,
    RemoveCartItemView,
    UpdateCartItemView,
)

urlpatterns = [
    path(
        "",
        CartView.as_view(),
        name="cart",
    ),
    path(
        "add/",
        AddToCartView.as_view(),
        name="cart-add",
    ),
    path(
        "items/<int:pk>/",
        UpdateCartItemView.as_view(),
        name="cart-item-update",
    ),
    path(
        "items/<int:pk>/remove/",
        RemoveCartItemView.as_view(),
        name="cart-item-remove",
    ),
]