from rest_framework import viewsets
from rest_framework.serializers import Serializer

from core.enums import ViewAction
from offers.models import Offer
from offers.serializers import OfferDetailSerializer, OfferListSerializer


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.select_related("buyer", "car")

    def get_serializer_class(self) -> type[Serializer]:
        if self.action == ViewAction.RETRIEVE:
            return OfferDetailSerializer
        return OfferListSerializer
