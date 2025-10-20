from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cars.views import BodyTypeViewSet, CarBrandViewSet, CarViewSet

router = DefaultRouter()
router.register("brands", CarBrandViewSet)
router.register("body-types", BodyTypeViewSet)
router.register("cars", CarViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
