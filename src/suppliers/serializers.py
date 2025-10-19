from typing import Any

from rest_framework import serializers

from cars.serializers import CarDetailSerializer, CarListSerializer
from suppliers.models import (
    Supplier,
    SupplierOffer,
    SupplierPromotion,
    SupplierSaleHistory,
)


class SupplierSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True, initial=True)

    class Meta:
        model = Supplier
        fields = [
            "id",
            "name",
            "founded_year",
            "country",
            "contact_email",
            "description",
            "created_at",
            "updated_at",
            "is_active",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SupplierOfferListSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True, initial=True)

    class Meta:
        model = SupplierOffer
        fields = [
            "id",
            "supplier",
            "car",
            "price",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SupplierOfferDetailSerializer(serializers.ModelSerializer):
    supplier = SupplierSerializer(read_only=True)
    car = CarDetailSerializer(read_only=True)

    class Meta:
        model = SupplierOffer
        fields = [
            "id",
            "supplier",
            "car",
            "price",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SupplierPromotionListSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True, initial=True)

    class Meta:
        model = SupplierPromotion
        fields = [
            "id",
            "supplier",
            "title",
            "discount_percent",
            "start_date",
            "end_date",
            "cars",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(
                {"error": "End date must be after start date."}
            )
        return attrs


class SupplierPromotionDetailSerializer(serializers.ModelSerializer):
    supplier = SupplierSerializer(read_only=True)
    cars = CarListSerializer(many=True, read_only=True)

    class Meta:
        model = SupplierPromotion
        fields = [
            "id",
            "supplier",
            "title",
            "description",
            "cars",
            "discount_percent",
            "start_date",
            "end_date",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SupplierSaleHistoryListSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True, initial=True)

    class Meta:
        model = SupplierSaleHistory
        fields = [
            "id",
            "supplier",
            "dealership",
            "car",
            "price",
            "sale_date",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SupplierSaleHistoryDetailSerializer(serializers.ModelSerializer):
    supplier = SupplierSerializer(read_only=True)
    car = CarDetailSerializer(read_only=True)

    class Meta:
        model = SupplierSaleHistory
        fields = [
            "id",
            "supplier",
            "dealership",
            "car",
            "price",
            "sale_date",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "sale_date", "created_at", "updated_at"]
