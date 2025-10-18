from rest_framework import mixins, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView

from users.models import User, UserProfile
from users.serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    UserSerializer,
)
from users.services.email_service import confirm_user_email


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().select_related("user_profile")
    serializer_class = UserSerializer

    def get_serializer_class(self) -> type[Serializer]:
        if self.action == "create":
            return RegisterSerializer
        return UserSerializer


class UserProfileViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class ConfirmEmailView(APIView):
    def get(self, request: Request, token: str) -> Response:
        return confirm_user_email(token)
