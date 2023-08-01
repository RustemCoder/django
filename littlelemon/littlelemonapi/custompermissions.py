from rest_framework import permissions

class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name="Customer").exists():
            return True


class IsDeliveryCrew(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name="Customer").exists():
            return True