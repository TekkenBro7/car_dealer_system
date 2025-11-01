from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView

from core.enums import ViewAction
from users.filters import UserFilter, UserProfileFilter
from users.models import User, UserProfile
from users.permissions import IsAdminOrSelf, IsAdminUser
from users.serializers import (
    BuyerReportSerializer,
    ChangePasswordSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    UserProfileSerializer,
    UserSerializer,
)
from users.services.email_service import confirm_user_email, confirm_user_username


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
    permission_classes = [AllowAny]

    def get(self, request: Request, token: str) -> Response:
        return confirm_user_email(token)


class ConfirmUsernameView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request, token: str) -> Response:
        return confirm_user_username(token)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response(
            {"OK": "Password changed successfully."}, status=status.HTTP_200_OK
        )


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"OK": "Password reset link sent to your email."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"OK": "Password successfully reset."},
            status=status.HTTP_200_OK,
        )


class BuyerReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = BuyerReportSerializer
    permission_classes = [IsAdminUser]
