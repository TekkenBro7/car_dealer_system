from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.views.auth import LogoutView, VerifyAuthView
from users.views.users import ConfirmEmailView, UserProfileViewSet, UserViewSet

router = DefaultRouter()
router.register("users", UserViewSet)
router.register("profiles", UserProfileViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("confirm-email/<str:token>/", ConfirmEmailView.as_view()),
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", LogoutView.as_view(), name="auth_logout"),
    path("auth/verify/", VerifyAuthView.as_view(), name="auth_verify"),
]
