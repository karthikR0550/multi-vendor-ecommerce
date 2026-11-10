from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    message = "Admin access required."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "ADMIN"
        )


class IsShopOwner(BasePermission):
    message = "Shop owner access required."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "SHOP_OWNER"
        )


class IsCustomer(BasePermission):
    message = "Customer access required."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "CUSTOMER"
        )


class IsDelivery(BasePermission):
    message = "Delivery access required."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "DELIVERY"
        )