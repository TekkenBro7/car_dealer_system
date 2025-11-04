from decimal import Decimal

import pytest
from django.db import IntegrityError

from cars.models import BodyType, Car, CarBrand
from dealerships.models import Dealership, DealershipSaleHistory
from offers.models import Offer, OfferStatus
from users.models import User, UserProfile


@pytest.fixture
def car_brand() -> CarBrand:
    return CarBrand.objects.create(name="Toyota", country="JP")


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


@pytest.mark.django_db
class TestOfferSignals:
    def test_create_dealership_sale_history_signal(
        self, test_buyer: User, test_car: Car
    ) -> None:
        dealership = Dealership.objects.create(
            name="Test Dealership", country="JP", city="Tokyo", balance=100000.00
        )

        offer = Offer.objects.create(
            buyer=test_buyer,
            car=test_car,
            dealership=dealership,
            max_price=Decimal("30000.00"),
            status=OfferStatus.PENDING,
        )

        assert not DealershipSaleHistory.objects.filter(
            dealership=dealership, car=test_car, buyer=test_buyer
        ).exists()

        offer.actual_price = Decimal("30000.00")
        offer.status = OfferStatus.ACCEPTED
        offer.save()

        sale_history_qs = DealershipSaleHistory.objects.filter(
            dealership=dealership, car=test_car, buyer=test_buyer, price=offer.max_price
        )
        assert sale_history_qs.exists()
        sale_history = sale_history_qs.get()
        assert sale_history.price == Decimal("30000.00")

    def test_signal_not_triggered_for_pending_offer(
        self, test_buyer: User, test_car: Car
    ) -> None:
        dealership = Dealership.objects.create(
            name="Pending Dealership", country="JP", city="Osaka", balance=50000.00
        )

        Offer.objects.create(
            buyer=test_buyer,
            car=test_car,
            dealership=dealership,
            max_price=20000.00,
            status=OfferStatus.PENDING,
        )

        assert not DealershipSaleHistory.objects.filter(
            buyer=test_buyer, car=test_car
        ).exists()

        assert UserProfile.objects.filter(user=test_buyer).exists()
