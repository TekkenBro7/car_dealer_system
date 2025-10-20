from rest_framework import viewsets
from rest_framework.serializers import Serializer

from cars.models import BodyType, Car, CarBrand
from cars.serializers import (
    BodyTypeSerializer,
    CarBrandSerializer,
    CarDetailSerializer,
    CarListSerializer,
)


class CarBrandViewSet(viewsets.ModelViewSet):
    queryset = CarBrand.objects.all()
    serializer_class = CarBrandSerializer


class BodyTypeViewSet(viewsets.ModelViewSet):
    queryset = BodyType.objects.all()
    serializer_class = BodyTypeSerializer


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.select_related("brand", "body_type")

    def get_serializer_class(self) -> type[Serializer]:
        if self.action == "retrieve":
            return CarDetailSerializer
        return CarListSerializer
