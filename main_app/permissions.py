from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Дозвіл, що дозволяє лише адміністраторам редагувати об'єкти.
    """

    def has_permission(self, request, view):
        # Дозвіл тільки для адміністраторів, для інших тільки читання.
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
