from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import ConfirmEmailView, UserProfileViewSet, UserViewSet

router = DefaultRouter()
router.register("users", UserViewSet)
router.register("profiles", UserProfileViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("confirm-email/<str:token>/", ConfirmEmailView.as_view()),
]
