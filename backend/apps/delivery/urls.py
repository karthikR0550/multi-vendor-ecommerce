from django.urls import path

from .views import (
    AssignDeliveryView,
    CompleteDeliveryView,
    DeliveryAssignmentListView,
    DeliveryPersonListView,
    PackedOrdersListView,
    MyDeliveryListView,
    OutForDeliveryView,
    PickUpDeliveryView,
)


urlpatterns = [

    # =========================
    # ADMIN
    # =========================

    path(
        "admin/assign/",
        AssignDeliveryView.as_view(),
        name="assign-delivery",
    ),

    path(
        "admin/assignments/",
        DeliveryAssignmentListView.as_view(),
        name="delivery-assignments",
    ),


    # =========================
    # DELIVERY PERSON
    # =========================

    path(
        "my-deliveries/",
        MyDeliveryListView.as_view(),
        name="my-deliveries",
    ),

    path(
        "<int:pk>/pickup/",
        PickUpDeliveryView.as_view(),
        name="pickup-delivery",
    ),

    path(
        "<int:pk>/out-for-delivery/",
        OutForDeliveryView.as_view(),
        name="out-for-delivery",
    ),

    path(
        "<int:pk>/delivered/",
        CompleteDeliveryView.as_view(),
        name="complete-delivery",
    ),
    path(
    "admin/delivery-persons/",
    DeliveryPersonListView.as_view(),
    name="delivery-persons",
),
path(
    "admin/packed-orders/",
    PackedOrdersListView.as_view(),
    name="packed-orders",
),
]