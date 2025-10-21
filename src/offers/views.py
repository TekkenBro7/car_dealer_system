from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.serializers import Serializer

from offers.filters import OfferFilter
from offers.models import Offer
from offers.serializers import OfferDetailSerializer, OfferListSerializer


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.select_related("buyer", "car")
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ["buyer__username", "car__model_name", "status", "is_active"]
    ordering_fields = ["max_price", "created_at", "updated_at", "is_active"]
    ordering = ["-is_active", "-created_at"]

    def get_serializer_class(self) -> type[Serializer]:
        if self.action == "retrieve":
            return OfferDetailSerializer
        return OfferListSerializer
