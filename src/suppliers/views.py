from rest_framework import viewsets
from rest_framework.serializers import Serializer

from core.enums import ViewAction
from suppliers.models import (
    Supplier,
    SupplierOffer,
    SupplierPromotion,
    SupplierSaleHistory,
)
from suppliers.serializers import (
    SupplierOfferDetailSerializer,
    SupplierOfferListSerializer,
    SupplierPromotionDetailSerializer,
    SupplierPromotionListSerializer,
    SupplierSaleHistoryDetailSerializer,
    SupplierSaleHistoryListSerializer,
    SupplierSerializer,
)


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class SupplierOfferViewSet(viewsets.ModelViewSet):
    queryset = SupplierOffer.objects.select_related("supplier", "car")

    def get_serializer_class(self) -> type[Serializer]:
        if self.action == ViewAction.RETRIEVE:
            return SupplierOfferDetailSerializer
        return SupplierOfferListSerializer


class SupplierPromotionViewSet(viewsets.ModelViewSet):
    queryset = SupplierPromotion.objects.prefetch_related("cars").select_related(
        "supplier"
    )

    def get_serializer_class(self) -> type[Serializer]:
        if self.action == ViewAction.RETRIEVE:
            return SupplierPromotionDetailSerializer
        return SupplierPromotionListSerializer


class SupplierSaleHistoryViewSet(viewsets.ModelViewSet):
    queryset = SupplierSaleHistory.objects.select_related(
        "supplier", "car", "dealership"
    )

    def get_serializer_class(self) -> type[Serializer]:
        if self.action == ViewAction.RETRIEVE:
            return SupplierSaleHistoryDetailSerializer
        return SupplierSaleHistoryListSerializer
