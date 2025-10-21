import django_filters
from django.db.models import QuerySet

from cars.models import Car
from suppliers.models import (
    Supplier,
    SupplierOffer,
    SupplierPromotion,
    SupplierSaleHistory,
)


class SupplierFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    country = django_filters.CharFilter(method="filter_country")

    class Meta:
        model = Supplier
        fields = ["name", "country"]

    def filter_country(self, queryset: QuerySet, _name: str, value: str) -> QuerySet:
        value = value.upper()
        return queryset.filter(country=value)


class SupplierOfferFilter(django_filters.FilterSet):
    supplier = django_filters.CharFilter(
        field_name="supplier__name", lookup_expr="icontains"
    )
    car = django_filters.CharFilter(
        field_name="car__model_name", lookup_expr="icontains"
    )
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = SupplierOffer
        fields = ["supplier", "car", "price_min", "price_max"]


class SupplierPromotionFilter(django_filters.FilterSet):
    supplier = django_filters.CharFilter(
        field_name="supplier__name", lookup_expr="icontains"
    )
    title = django_filters.CharFilter(lookup_expr="icontains")
    start_date_after = django_filters.DateFilter(
        field_name="start_date", lookup_expr="gte"
    )
    end_date_before = django_filters.DateFilter(
        field_name="end_date", lookup_expr="lte"
    )

    cars = django_filters.ModelMultipleChoiceFilter(
        queryset=Car.objects.all(),
        field_name="cars",
        to_field_name="id",
        conjoined=False,
    )

    class Meta:
        model = SupplierPromotion
        fields = ["supplier", "title", "start_date", "end_date", "cars"]


class SupplierSaleHistoryFilter(django_filters.FilterSet):
    supplier = django_filters.CharFilter(
        field_name="supplier__name", lookup_expr="icontains"
    )
    dealership = django_filters.CharFilter(
        field_name="dealership__name", lookup_expr="icontains"
    )
    car = django_filters.CharFilter(
        field_name="car__model_name", lookup_expr="icontains"
    )
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = SupplierSaleHistory
        fields = ["supplier", "dealership", "car", "price_min", "price_max"]
