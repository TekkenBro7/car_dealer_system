from typing import Any

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from core.enums import ViewAction


class IsAdminOrSelf(permissions.BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool:
        action = getattr(view, "action", None)

        if action == ViewAction.CREATE:
            return (
                not request.user.is_authenticated
                or getattr(request.user, "role", None) == "admin"
            )

        if not request.user.is_authenticated:
            return False

        if action == ViewAction.LIST:
            return request.user.role == "admin"

        return True

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        if getattr(request.user, "role", None) == "admin":
            return True

        return obj == request.user
