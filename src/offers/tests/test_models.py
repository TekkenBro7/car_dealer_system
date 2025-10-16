import pytest
from django.db import IntegrityError

from cars.models import BodyType, Car, CarBrand
from offers.models import Offer, OfferStatus
from users.models import User


@pytest.fixture
def car_brand() -> CarBrand:
    return CarBrand.objects.create(name="Toyota", country="Japan")


@pytest.fixture
def body_type() -> BodyType:
    return BodyType.objects.create(name="Sedan")


@pytest.fixture
def test_car(car_brand: CarBrand, body_type: BodyType) -> Car:
    return Car.objects.create(brand=car_brand, body_type=body_type, model_name="Camry")


@pytest.fixture
def test_buyer() -> User:
    return User.objects.create_user(
        username="test_buyer", email="test_buyer@example.com", password="testpass123"
    )


@pytest.fixture
def test_offer_data(test_buyer: User, test_car: Car) -> dict:
    return {
        "buyer": test_buyer,
        "car": test_car,
        "max_price": 25000.00,
        "status": OfferStatus.ACCEPTED,
    }


@pytest.mark.django_db
class TestOfferModel:
    def test_offer_creation(self, test_offer_data: dict) -> None:
        offer = Offer.objects.create(**test_offer_data)

        assert offer.buyer == test_offer_data["buyer"]
        assert offer.car == test_offer_data["car"]
        assert offer.max_price == test_offer_data["max_price"]
        assert offer.status == OfferStatus.ACCEPTED
        assert offer.is_active is True
        assert offer.created_at is not None
        assert offer.updated_at is not None

    def test_offer_string_representation(self, test_offer_data: dict) -> None:
        offer = Offer.objects.create(**test_offer_data)

        expected_str = (
            f"Offer by {test_offer_data['buyer'].username} for "
            f"{test_offer_data['car'].model_name} up to ${test_offer_data['max_price']}"
        )
        assert str(offer) == expected_str

    def test_offer_default_status(self, test_buyer: User, test_car: Car) -> None:
        offer = Offer.objects.create(buyer=test_buyer, car=test_car, max_price=20000.00)

        assert offer.status == OfferStatus.PENDING

    def test_offer_status_choices(self) -> None:
        choices = dict(OfferStatus.choices)

        assert choices["pending"] == "Pending"
        assert choices["accepted"] == "Accepted"
        assert choices["rejected"] == "Rejected"
        assert choices["cancelled"] == "Cancelled"

    def test_offer_without_buyer_raises_error(self, test_car: Car) -> None:
        with pytest.raises(IntegrityError):
            Offer.objects.create(car=test_car, max_price=10000.00)

    def test_offer_without_car_raises_error(self, test_buyer: User) -> None:
        with pytest.raises(IntegrityError):
            Offer.objects.create(buyer=test_buyer, max_price=10000.00)
