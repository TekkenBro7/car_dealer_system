from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.serializers import Serializer

from cars.filters import CarFilter
from cars.models import BodyType, Car, CarBrand
from cars.permissions import IsAdminOrReadOnly
from cars.serializers import (
    BodyTypeSerializer,
    CarBrandSerializer,
    CarDetailSerializer,
    CarListSerializer,
)
from core.enums import ViewAction


class CarBrandViewSet(viewsets.ModelViewSet):
    queryset = CarBrand.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = CarBrandSerializer


class BodyTypeViewSet(viewsets.ModelViewSet):
    queryset = BodyType.objects.all()
    serializer_class = BodyTypeSerializer
    permission_classes = [IsAdminOrReadOnly]


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.select_related("brand", "body_type")
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CarFilter
    search_fields = ["model_name", "brand__name", "body_type__name", "is_active"]
    ordering_fields = ["created_at", "updated_at", "model_name", "is_active"]
    ordering = ["-is_active", "-created_at"]

    def get_serializer_class(self) -> type[Serializer]:
        if self.action == ViewAction.RETRIEVE:
            return CarDetailSerializer
        return CarListSerializer
