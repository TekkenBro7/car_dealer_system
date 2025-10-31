from typing import Any

from django.db.models import Sum
from rest_framework import serializers

from cars.serializers import CarDetailSerializer, CarListSerializer
from dealerships.models import (
    Dealership,
    DealershipPromotion,
    DealershipSaleHistory,
    Inventory,
    PreferredModel,
)
from users.serializers import UserSerializer


class DealershipSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True, initial=True)

    class Meta:
        model = Dealership
        fields = [
            "id",
            "name",
            "country",
            "city",
            "balance",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class InventoryListSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True, initial=True)

    class Meta:
        model = Inventory
        fields = [
            "id",
            "dealership",
            "car",
            "quantity",
            "price",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class InventoryDetailSerializer(serializers.ModelSerializer):
    dealership = DealershipSerializer(read_only=True)
    car = CarDetailSerializer(read_only=True)

    class Meta:
        model = Inventory
        fields = [
            "id",
            "dealership",
            "car",
            "quantity",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PreferredModelListSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True, initial=True)

    class Meta:
        model = PreferredModel
        fields = [
            "id",
            "dealership",
            "car",
            "reason",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PreferredModelDetailSerializer(serializers.ModelSerializer):
    dealership = DealershipSerializer(read_only=True)
    car = CarListSerializer(read_only=True)

    class Meta:
        model = PreferredModel
        fields = [
            "id",
            "dealership",
            "car",
            "reason",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DealershipPromotionListSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True, initial=True)

    class Meta:
        model = DealershipPromotion
        fields = [
            "id",
            "dealership",
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

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(
                {"error": "End date must be after start date."}
            )
        return attrs


class DealershipPromotionDetailSerializer(serializers.ModelSerializer):
    dealership = DealershipSerializer(read_only=True)
    cars = CarListSerializer(many=True, read_only=True)

    class Meta:
        model = DealershipPromotion
        fields = [
            "id",
            "dealership",
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


class DealershipSaleHistoryListSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True, initial=True)

    class Meta:
        model = DealershipSaleHistory
        fields = [
            "id",
            "dealership",
            "car",
            "buyer",
            "price",
            "sale_date",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "sale_date", "created_at", "updated_at"]


class DealershipSaleHistoryDetailSerializer(serializers.ModelSerializer):
    dealership = DealershipSerializer(read_only=True)
    car = CarDetailSerializer(read_only=True)
    buyer = UserSerializer(read_only=True)

    class Meta:
        model = DealershipSaleHistory
        fields = [
            "id",
            "dealership",
            "car",
            "buyer",
            "price",
            "sale_date",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "sale_date", "created_at", "updated_at"]


class DealershipReportSerializer(serializers.ModelSerializer):
    total_sales = serializers.SerializerMethodField()
    total_profit = serializers.SerializerMethodField()
    unique_buyers = serializers.SerializerMethodField()

    class Meta:
        model = Dealership
        fields = [
            "id",
            "name",
            "country",
            "city",
            "total_sales",
            "total_profit",
            "unique_buyers",
        ]

    def get_total_sales(self, obj: Dealership) -> int:
        return obj.sales_history.count()

    def get_total_profit(self, obj: Dealership) -> float:
        total = obj.sales_history.aggregate(total=Sum("price"))["total"]
        return float(total) if total else 0.0

    def get_unique_buyers(self, obj: Dealership) -> int:
        return obj.sales_history.values("buyer").distinct().count()
