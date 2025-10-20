from rest_framework import viewsets
from rest_framework.serializers import Serializer

from offers.models import Offer
from offers.serializers import OfferDetailSerializer, OfferListSerializer


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.select_related("buyer", "car")

    def get_serializer_class(self) -> type[Serializer]:
        if self.action == "retrieve":
            return OfferDetailSerializer
        return OfferListSerializer
