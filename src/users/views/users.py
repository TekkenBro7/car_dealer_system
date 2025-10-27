from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView

from core.enums import ViewAction
from users.filters import UserFilter, UserProfileFilter
from users.models import User, UserProfile
from users.permissions import IsAdminOrSelf
from users.serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    UserSerializer,
)
from users.services.email_service import confirm_user_email


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().select_related("user_profile")
    permission_classes = [IsAdminOrSelf]
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UserFilter
    search_fields = ["username", "email", "is_active"]
    ordering_fields = ["username", "email", "date_joined", "is_active"]
    ordering = ["-is_active", "-date_joined"]

    def get_serializer_class(self) -> type[Serializer]:
        if self.action == ViewAction.CREATE:
            return RegisterSerializer
        return UserSerializer


class UserProfileViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = UserProfile.objects.all()
    permission_classes = [IsAdminOrSelf]
    serializer_class = UserProfileSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UserProfileFilter
    search_fields = ["user__username", "is_active"]
    ordering_fields = ["balance", "total_spent", "purchase_count", "is_active"]
    ordering = ["-is_active", "-balance"]


class ConfirmEmailView(APIView):
    def get(self, request: Request, token: str) -> Response:
        return confirm_user_email(token)
