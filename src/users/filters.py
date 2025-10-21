import django_filters

from users.models import User, UserProfile, UserRoles


class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(lookup_expr="icontains")
    email = django_filters.CharFilter(lookup_expr="icontains")
    role = django_filters.ChoiceFilter(choices=UserRoles.choices)
    email_confirmed = django_filters.BooleanFilter()

    class Meta:
        model = User
        fields = ["username", "email", "role", "email_confirmed"]


class UserProfileFilter(django_filters.FilterSet):
    user__username = django_filters.CharFilter(
        field_name="user__username", lookup_expr="icontains"
    )
    balance_min = django_filters.NumberFilter(field_name="balance", lookup_expr="gte")
    balance_max = django_filters.NumberFilter(field_name="balance", lookup_expr="lte")
    total_spent_min = django_filters.NumberFilter(
        field_name="total_spent", lookup_expr="gte"
    )
    total_spent_max = django_filters.NumberFilter(
        field_name="total_spent", lookup_expr="lte"
    )
    purchase_count_min = django_filters.NumberFilter(
        field_name="purchase_count", lookup_expr="gte"
    )
    purchase_count_max = django_filters.NumberFilter(
        field_name="purchase_count", lookup_expr="lte"
    )

    class Meta:
        model = UserProfile
        fields = [
            "user__username",
            "balance_min",
            "balance_max",
            "total_spent_min",
            "total_spent_max",
            "purchase_count_min",
            "purchase_count_max",
        ]
