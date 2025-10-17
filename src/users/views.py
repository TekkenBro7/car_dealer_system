from rest_framework import mixins, status, viewsets
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
from users.utils import email_verification


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
        user_pk = email_verification.verify_email_token(token)
        if not user_pk:
            return Response(
                {"detail": "The link is invalid or outdated."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            return Response(
                {"detail": "The user was not found."}, status=status.HTTP_404_NOT_FOUND
            )

        user.email_confirmed = True
        user.save()
        return Response(
            {"detail": "Email successfully confirmed."}, status=status.HTTP_200_OK
        )
