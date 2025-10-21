import django_filters

from offers.models import Offer


class OfferFilter(django_filters.FilterSet):
    buyer = django_filters.CharFilter(
        field_name="buyer__username", lookup_expr="icontains"
    )
    car = django_filters.CharFilter(
        field_name="car__model_name", lookup_expr="icontains"
    )

    max_price_min = django_filters.NumberFilter(
        field_name="max_price", lookup_expr="gte"
    )
    max_price_max = django_filters.NumberFilter(
        field_name="max_price", lookup_expr="lte"
    )

    status = django_filters.CharFilter(field_name="status", lookup_expr="icontains")

    created_after = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte"
    )

    class Meta:
        model = Offer
        fields = [
            "buyer",
            "car",
            "max_price_min",
            "max_price_max",
            "status",
            "created_after",
            "created_before",
        ]
