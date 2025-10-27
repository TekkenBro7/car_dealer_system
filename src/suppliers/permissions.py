from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS
from rest_framework.request import Request
from rest_framework.views import APIView


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and getattr(request.user, "role", None) == "admin"
        )
