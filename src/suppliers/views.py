from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.serializers import Serializer

from suppliers.filters import (
    SupplierFilter,
    SupplierOfferFilter,
    SupplierPromotionFilter,
    SupplierSaleHistoryFilter,
)
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
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SupplierFilter
    search_fields = ["name", "country", "is_active"]
    ordering_fields = ["founded_year", "created_at", "updated_at", "is_active"]
    ordering = ["-is_active", "-created_at"]


class SupplierOfferViewSet(viewsets.ModelViewSet):
    queryset = SupplierOffer.objects.select_related("supplier", "car")
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SupplierOfferFilter
    search_fields = ["supplier__name", "car__model_name", "is_active"]
    ordering_fields = ["price", "created_at", "updated_at", "is_active"]
    ordering = ["-is_active", "-created_at"]

    def get_serializer_class(self) -> type[Serializer]:
        if self.action == "retrieve":
            return SupplierOfferDetailSerializer
        return SupplierOfferListSerializer


class SupplierPromotionViewSet(viewsets.ModelViewSet):
    queryset = SupplierPromotion.objects.prefetch_related("cars").select_related(
        "supplier"
    )
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SupplierPromotionFilter
    search_fields = ["title", "supplier__name", "description", "is_active"]
    ordering_fields = ["discount_percent", "start_date", "end_date", "is_active"]
    ordering = ["-is_active", "-start_date"]

    def get_serializer_class(self) -> type[Serializer]:
        if self.action == "retrieve":
            return SupplierPromotionDetailSerializer
        return SupplierPromotionListSerializer


class SupplierSaleHistoryViewSet(viewsets.ModelViewSet):
    queryset = SupplierSaleHistory.objects.select_related(
        "supplier", "car", "dealership"
    )
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SupplierSaleHistoryFilter
    search_fields = [
        "supplier__name",
        "dealership__name",
        "car__model_name",
        "is_active",
    ]
    ordering_fields = ["price", "sale_date", "is_active"]
    ordering = ["-is_active", "-sale_date"]

    def get_serializer_class(self) -> type[Serializer]:
        if self.action == "retrieve":
            return SupplierSaleHistoryDetailSerializer
        return SupplierSaleHistoryListSerializer
