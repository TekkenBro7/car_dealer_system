from typing import Any

import pytest

from cars.models import BodyType, Car, CarBrand
from offers.models import Offer, OfferStatus
from offers.serializers import OfferDetailSerializer, OfferListSerializer
from users.models import User


@pytest.fixture
def car_brand() -> CarBrand:
    return CarBrand.objects.create(name="Toyota", country="JP")


@pytest.fixture
def body_type() -> BodyType:
    return BodyType.objects.create(name="Sedan")


@pytest.fixture
def car(car_brand: CarBrand, body_type: BodyType) -> Car:
    return Car.objects.create(brand=car_brand, model_name="Camry", body_type=body_type)


@pytest.fixture
def user() -> User:
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )


@pytest.fixture
def offer(user: User, car: Car) -> Offer:
    return Offer.objects.create(
        buyer=user,
        car=car,
        max_price=25000.00,
    )


@pytest.mark.django_db
class TestOfferListSerializer:
    @pytest.fixture
    def valid_data(self, user: User, car: Car) -> dict[str, Any]:
        return {
            "buyer": user.id,
            "car": car.id,
            "max_price": 30000.00,
        }

    def test_valid_serializer_data(self, valid_data: dict[str, Any]) -> None:
        serializer = OfferListSerializer(data=valid_data)
        assert serializer.is_valid()

    def test_required_fields(self, valid_data: dict[str, Any]) -> None:
        required_fields = ["buyer", "car", "max_price"]

        for field in required_fields:
            invalid_data = valid_data.copy()
            del invalid_data[field]

            serializer = OfferListSerializer(data=invalid_data)
            assert not serializer.is_valid()
            assert field in serializer.errors

    def test_max_price_validation(self, valid_data: dict[str, Any]) -> None:
        invalid_data = valid_data.copy()
        invalid_data["max_price"] = -100.00

        serializer = OfferListSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert "max_price" in serializer.errors

        invalid_data["max_price"] = 0.00
        serializer = OfferListSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert "max_price" in serializer.errors

    def test_status_validation(self, valid_data: dict[str, Any]) -> None:
        invalid_data = valid_data.copy()
        invalid_data["status"] = "invalid_status"

        serializer = OfferListSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert "status" in serializer.errors

    def test_create_offer(
        self, valid_data: dict[str, Any], user: User, car: Car
    ) -> None:
        serializer = OfferListSerializer(data=valid_data)
        assert serializer.is_valid()

        offer_obj = serializer.save()
        assert offer_obj.buyer == user
        assert offer_obj.car == car
        assert offer_obj.max_price == 30000.00
        assert offer_obj.status == OfferStatus.PENDING
        assert offer_obj.is_active is True

    def test_serializer_fields(self, offer: Offer) -> None:
        serializer = OfferListSerializer(instance=offer)

        expected_fields = {
            "id",
            "buyer",
            "car",
            "max_price",
            "status",
            "created_at",
            "updated_at",
            "is_active",
        }

        assert serializer.data.keys() == expected_fields


@pytest.mark.django_db
class TestOfferDetailSerializer:
    def test_serializer_fields(self, offer: Offer) -> None:
        serializer = OfferDetailSerializer(instance=offer)

        expected_fields = {
            "id",
            "buyer",
            "car",
            "max_price",
            "status",
            "created_at",
            "updated_at",
            "is_active",
        }

        assert serializer.data.keys() == expected_fields

    def test_nested_serializers(self, offer: Offer) -> None:
        serializer = OfferDetailSerializer(instance=offer)

        assert isinstance(serializer.data["buyer"], dict)
        assert isinstance(serializer.data["car"], dict)

        assert serializer.data["buyer"]["username"] == offer.buyer.username
        assert "model_name" in serializer.data["car"]
