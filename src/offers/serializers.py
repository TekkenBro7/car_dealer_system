from rest_framework import serializers

from cars.serializers import CarDetailSerializer
from offers.models import Offer
from users.serializers import UserSerializer


class OfferListSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True, initial=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "buyer",
            "car",
            "max_price",
            "status",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class OfferDetailSerializer(serializers.ModelSerializer):
    buyer = UserSerializer(read_only=True)
    car = CarDetailSerializer(read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "buyer",
            "car",
            "max_price",
            "status",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
