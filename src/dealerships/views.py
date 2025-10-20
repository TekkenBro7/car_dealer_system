from rest_framework import viewsets
from rest_framework.serializers import Serializer

from dealerships.models import (
    Dealership,
    DealershipPromotion,
    DealershipSaleHistory,
    Inventory,
    PreferredModel,
)
from dealerships.serializers import (
    DealershipPromotionDetailSerializer,
    DealershipPromotionListSerializer,
    DealershipSaleHistoryDetailSerializer,
    DealershipSaleHistoryListSerializer,
    DealershipSerializer,
    InventoryDetailSerializer,
    InventoryListSerializer,
    PreferredModelDetailSerializer,
    PreferredModelListSerializer,
)


class DealershipViewSet(viewsets.ModelViewSet):
    queryset = Dealership.objects.all()
    serializer_class = DealershipSerializer


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.select_related("dealership", "car")

    def get_serializer_class(self) -> type[Serializer]:
        if self.action == "retrieve":
            return InventoryDetailSerializer
        return InventoryListSerializer


class PreferredModelViewSet(viewsets.ModelViewSet):
    queryset = PreferredModel.objects.select_related("dealership", "car")

    def get_serializer_class(self) -> type[Serializer]:
        if self.action == "retrieve":
            return PreferredModelDetailSerializer
        return PreferredModelListSerializer


class DealershipPromotionViewSet(viewsets.ModelViewSet):
    queryset = DealershipPromotion.objects.prefetch_related("cars").select_related(
        "dealership"
    )

    def get_serializer_class(self) -> type[Serializer]:
        if self.action == "retrieve":
            return DealershipPromotionDetailSerializer
        return DealershipPromotionListSerializer


class DealershipSaleHistoryViewSet(viewsets.ModelViewSet):
    queryset = DealershipSaleHistory.objects.select_related(
        "dealership", "car", "buyer"
    )

    def get_serializer_class(self) -> type[Serializer]:
        if self.action == "retrieve":
            return DealershipSaleHistoryDetailSerializer
        return DealershipSaleHistoryListSerializer
