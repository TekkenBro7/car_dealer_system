from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.views.auth import LogoutView, VerifyAuthView
from users.views.users import (
    BuyerReportViewSet,
    ChangePasswordView,
    ConfirmEmailView,
    ConfirmUsernameView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    UserProfileViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register("users", UserViewSet)
router.register("profiles", UserProfileViewSet)
router.register("buyer-reports", BuyerReportViewSet, basename="buyer-report")


urlpatterns = [
    path("", include(router.urls)),
    path("auth/confirm-email/<str:token>/", ConfirmEmailView.as_view()),
    path("auth/confirm-username/<str:token>/", ConfirmUsernameView.as_view()),
    path("auth/login/", TokenObtainPairView.as_view()),
    path("auth/refresh/", TokenRefreshView.as_view()),
    path("auth/logout/", LogoutView.as_view()),
    path("auth/verify/", VerifyAuthView.as_view()),
    path("auth/change-password/", ChangePasswordView.as_view()),
    path("auth/reset-password-request/", PasswordResetRequestView.as_view()),
    path("auth/reset-password/", PasswordResetConfirmView.as_view()),
]
