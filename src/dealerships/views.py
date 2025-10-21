from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.serializers import Serializer

from dealerships.filters import (
    DealershipFilter,
    DealershipPromotionFilter,
    DealershipSaleHistoryFilter,
    InventoryFilter,
    PreferredModelFilter,
)
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
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DealershipFilter
    search_fields = ["name", "city", "country"]
    ordering_fields = ["balance", "created_at", "updated_at", "is_active"]
    ordering = ["-is_active", "name"]


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.select_related("dealership", "car")
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = InventoryFilter
    search_fields = ["dealership__name", "car__model_name", "is_active"]
    ordering_fields = ["quantity", "created_at", "updated_at", "is_active"]
    ordering = ["-is_active", "-quantity"]

    def get_serializer_class(self) -> type[Serializer]:
        if self.action == "retrieve":
            return InventoryDetailSerializer
        return InventoryListSerializer


class PreferredModelViewSet(viewsets.ModelViewSet):
    queryset = PreferredModel.objects.select_related("dealership", "car")
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PreferredModelFilter
    search_fields = ["dealership__name", "car__model_name", "reason", "is_active"]
    ordering_fields = ["created_at", "updated_at", "is_active"]
    ordering = ["-is_active", "-created_at"]

    def get_serializer_class(self) -> type[Serializer]:
        if self.action == "retrieve":
            return PreferredModelDetailSerializer
        return PreferredModelListSerializer


class DealershipPromotionViewSet(viewsets.ModelViewSet):
    queryset = DealershipPromotion.objects.prefetch_related("cars").select_related(
        "dealership"
    )
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DealershipPromotionFilter
    search_fields = ["title", "dealership__name", "description", "is_active"]
    ordering_fields = ["discount_percent", "start_date", "end_date", "is_active"]
    ordering = ["-is_active", "-start_date"]

    def get_serializer_class(self) -> type[Serializer]:
        if self.action == "retrieve":
            return DealershipPromotionDetailSerializer
        return DealershipPromotionListSerializer


class DealershipSaleHistoryViewSet(viewsets.ModelViewSet):
    queryset = DealershipSaleHistory.objects.select_related(
        "dealership", "car", "buyer"
    )
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DealershipSaleHistoryFilter
    search_fields = [
        "buyer__username",
        "car__model_name",
        "dealership__name",
        "is_active",
    ]
    ordering_fields = ["price", "sale_date", "is_active"]
    ordering = ["-is_active", "-sale_date"]

    def get_serializer_class(self) -> type[Serializer]:
        if self.action == "retrieve":
            return DealershipSaleHistoryDetailSerializer
        return DealershipSaleHistoryListSerializer
