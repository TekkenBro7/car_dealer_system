import django_filters
from django.db.models import QuerySet

from cars.models import Car
from dealerships.models import (
    Dealership,
    DealershipPromotion,
    DealershipSaleHistory,
    Inventory,
    PreferredModel,
)


class DealershipFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    country = django_filters.CharFilter(method="filter_country")
    city = django_filters.CharFilter(lookup_expr="icontains")
    balance_min = django_filters.NumberFilter(field_name="balance", lookup_expr="gte")
    balance_max = django_filters.NumberFilter(field_name="balance", lookup_expr="lte")

    class Meta:
        model = Dealership
        fields = ["name", "country", "city", "balance_min", "balance_max"]

    def filter_country(self, queryset: QuerySet, _name: str, value: str) -> QuerySet:
        value = value.upper()
        return queryset.filter(country=value)


class InventoryFilter(django_filters.FilterSet):
    dealership = django_filters.CharFilter(
        field_name="dealership__name", lookup_expr="icontains"
    )
    car = django_filters.CharFilter(
        field_name="car__model_name", lookup_expr="icontains"
    )
    quantity_min = django_filters.NumberFilter(field_name="quantity", lookup_expr="gte")
    quantity_max = django_filters.NumberFilter(field_name="quantity", lookup_expr="lte")

    class Meta:
        model = Inventory
        fields = ["dealership", "car", "quantity_min", "quantity_max"]


class PreferredModelFilter(django_filters.FilterSet):
    dealership = django_filters.CharFilter(
        field_name="dealership__name", lookup_expr="icontains"
    )
    car = django_filters.CharFilter(
        field_name="car__model_name", lookup_expr="icontains"
    )

    class Meta:
        model = PreferredModel
        fields = ["dealership", "car"]


class DealershipPromotionFilter(django_filters.FilterSet):
    dealership = django_filters.CharFilter(
        field_name="dealership__name", lookup_expr="icontains"
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
        model = DealershipPromotion
        fields = ["dealership", "title", "start_date", "end_date", "cars"]


class DealershipSaleHistoryFilter(django_filters.FilterSet):
    dealership = django_filters.CharFilter(
        field_name="dealership__name", lookup_expr="icontains"
    )
    buyer = django_filters.CharFilter(
        field_name="buyer__username", lookup_expr="icontains"
    )
    car = django_filters.CharFilter(
        field_name="car__model_name", lookup_expr="icontains"
    )
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = DealershipSaleHistory
        fields = ["dealership", "buyer", "car", "price_min", "price_max"]
