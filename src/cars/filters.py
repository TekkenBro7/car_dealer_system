import django_filters

from cars.models import Car


class CarFilter(django_filters.FilterSet):
    brand = django_filters.CharFilter(field_name="brand__name", lookup_expr="icontains")
    body_type = django_filters.CharFilter(
        field_name="body_type__name", lookup_expr="icontains"
    )
    model_name = django_filters.CharFilter(lookup_expr="icontains")
    created_after = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte"
    )

    class Meta:
        model = Car
        fields = ["brand", "body_type", "model_name", "created_after", "created_before"]
