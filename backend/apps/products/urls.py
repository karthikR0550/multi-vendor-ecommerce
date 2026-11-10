from django.urls import path

from .views import (
    ApproveProductView,
    MyProductListView,
    MyProductManageView,
    PendingProductListView,
    ProductCreateView,
    ProductDetailView,
    ProductListView,
    RejectProductView,
    
)

urlpatterns = [
    # Shop owner
    path(
        "create/",
        ProductCreateView.as_view(),
        name="product-create",
    ),
    path(
        "my-products/",
        MyProductListView.as_view(),
        name="my-products",
    ),

path(
    "my-products/<int:pk>/",
    MyProductManageView.as_view(),
    name="my-product-manage",
),
    # Admin
    path(
        "admin/pending/",
        PendingProductListView.as_view(),
        name="pending-products",
    ),
    path(
        "admin/<int:pk>/approve/",
        ApproveProductView.as_view(),
        name="approve-product",
    ),
    path(
        "admin/<int:pk>/reject/",
        RejectProductView.as_view(),
        name="reject-product",
    ),
    # Customer catalog
path(
    "",
    ProductListView.as_view(),
    name="product-list",
),
path(
    "<int:pk>/",
    ProductDetailView.as_view(),
    name="product-detail",
),
]