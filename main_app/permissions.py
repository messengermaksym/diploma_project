from rest_framework import permissions

# Дозвіл тільки для адміністраторів, для інших тільки читання.
class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):

        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
