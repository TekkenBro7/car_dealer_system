from rest_framework import serializers

from cars.models import BodyType, Car, CarBrand


class CarBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarBrand
        fields = ["id", "name", "country", "created_at", "is_active", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class BodyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BodyType
        fields = ["id", "name", "created_at", "is_active", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class CarListSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True, initial=True)

    class Meta:
        model = Car
        fields = [
            "id",
            "model_name",
            "brand",
            "body_type",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CarDetailSerializer(serializers.ModelSerializer):
    brand = CarBrandSerializer(read_only=True)
    body_type = BodyTypeSerializer(read_only=True)

    class Meta:
        model = Car
        fields = [
            "id",
            "brand",
            "body_type",
            "model_name",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "is_active", "updated_at"]
