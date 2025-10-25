from rest_framework import status
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


class LogoutView(APIView):
    permission_classes: list[type[BasePermission]] = [AllowAny]

    def post(self, request: Request) -> Response:
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(
                {"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST
            )


class VerifyAuthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response({"detail": "Authenticated"}, status=status.HTTP_200_OK)
