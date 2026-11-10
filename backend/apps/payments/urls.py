from django.urls import path

from .views import (
    CancelOrderAndRefundView,
    CreateRazorpayOrderView,
    RazorpayWebhookView,
    VerifyRazorpayPaymentView,
)


urlpatterns = [
    path(
        "create-order/",
        CreateRazorpayOrderView.as_view(),
        name="create-razorpay-order",
    ),

    path(
        "verify/",
        VerifyRazorpayPaymentView.as_view(),
        name="verify-razorpay-payment",
    ),

    path(
    "orders/<int:order_id>/cancel/",
    CancelOrderAndRefundView.as_view(),
    name="cancel-order-refund",
),
path(
    "webhook/",
    RazorpayWebhookView.as_view(),
    name="razorpay-webhook",
),
]