from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Права доступа на изменение только у админа.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return request.user.is_admin


class IsAdminOrOwner(permissions.BasePermission):
    """
    Права доступа только у админа или владельца объекта.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return request.user.is_admin or (
                request.user == obj)
