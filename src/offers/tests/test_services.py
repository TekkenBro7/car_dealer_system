from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from cars.models import BodyType, Car, CarBrand
from dealerships.models import Dealership, DealershipPromotion, Inventory
from offers.models import Offer, OfferStatus
from offers.services.dealership_offers import apply_dealership_promotion_price
from offers.services.purchase import execute_offer_purchase
from users.models import User, UserProfile


@pytest.fixture
def test_buyer() -> User:
    return User.objects.create_user(
        username="test_buyer",
        email="buyer@example.com",
        password="testpass123",
        email_confirmed=True,
    )


@pytest.fixture
def test_car() -> Car:
    brand = CarBrand.objects.create(name="Toyota", country="JP")
    body_type = BodyType.objects.create(name="Sedan")
    return Car.objects.create(brand=brand, body_type=body_type, model_name="Camry")


@pytest.fixture
def test_dealership() -> Dealership:
    return Dealership.objects.create(
        name="Test Dealership",
        country="US",
        city="New York",
        balance=Decimal("100000.00"),
    )


@pytest.fixture
def test_inventory(test_dealership: Dealership, test_car: Car) -> Inventory:
    return Inventory.objects.create(
        dealership=test_dealership, car=test_car, quantity=5, price=Decimal("25000.00")
    )


@pytest.fixture
def test_offer(test_buyer: User, test_car: Car) -> Offer:
    return Offer.objects.create(
        buyer=test_buyer,
        car=test_car,
        max_price=Decimal("30000.00"),
        status=OfferStatus.PENDING,
    )


@pytest.mark.django_db
class TestDealershipOffers:
    # pylint: disable=unused-argument
    def test_apply_dealership_promotion_price_no_promotions(
        self, test_dealership: Dealership, test_car: Car, test_inventory: Inventory
    ) -> None:

        result = apply_dealership_promotion_price(
            test_dealership, test_car, timezone.now().date()
        )

        assert result == Decimal("25000.00")

    # pylint: disable=unused-argument
    def test_apply_dealership_promotion_price_with_global_promotion(
        self, test_dealership: Dealership, test_car: Car, test_inventory: Inventory
    ) -> None:
        DealershipPromotion.objects.create(
            dealership=test_dealership,
            title="Autumn Sale",
            discount_percent=10.00,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
        )

        result = apply_dealership_promotion_price(
            test_dealership, test_car, timezone.now().date()
        )

        assert result == Decimal("22500.00")

    # pylint: disable=unused-argument
    def test_apply_dealership_promotion_price_with_specific_car_promotion(
        self, test_dealership: Dealership, test_car: Car, test_inventory: Inventory
    ) -> None:
        promotion = DealershipPromotion.objects.create(
            dealership=test_dealership,
            title="Camry Special",
            discount_percent=Decimal("15.00"),
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
        )
        promotion.cars.add(test_car)

        result = apply_dealership_promotion_price(
            test_dealership, test_car, timezone.now().date()
        )

        assert result == Decimal("21250.00")

    def test_apply_dealership_promotion_price_car_not_in_inventory(
        self, test_dealership: Dealership, test_car: Car
    ) -> None:
        result = apply_dealership_promotion_price(
            test_dealership, test_car, timezone.now().date()
        )

        assert result is None

    # pylint: disable=unused-argument
    def test_apply_dealership_promotion_price_expired_promotion(
        self, test_dealership: Dealership, test_car: Car, test_inventory: Inventory
    ) -> None:
        DealershipPromotion.objects.create(
            dealership=test_dealership,
            title="Expired Sale",
            discount_percent=Decimal("20.00"),
            start_date=timezone.now().date() - timedelta(days=60),
            end_date=timezone.now().date() - timedelta(days=30),
        )

        result = apply_dealership_promotion_price(
            test_dealership, test_car, timezone.now().date()
        )

        assert result == Decimal("25000.00")

    # pylint: disable=unused-argument
    def test_apply_dealership_promotion_price_with_global_and_specific_car_promotion(
        self, test_dealership: Dealership, test_car: Car, test_inventory: Inventory
    ) -> None:
        promotion_specific = DealershipPromotion.objects.create(
            dealership=test_dealership,
            title="Camry Special",
            discount_percent=Decimal("15.00"),
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
        )
        promotion_specific.cars.add(test_car)

        DealershipPromotion.objects.create(
            dealership=test_dealership,
            title="Autumn Sale",
            discount_percent=10.00,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
        )

        result = apply_dealership_promotion_price(
            test_dealership, test_car, timezone.now().date()
        )

        assert result == Decimal("18750.00")


@pytest.mark.django_db
class TestPurchaseService:
    # pylint: disable=unused-argument
    def test_execute_offer_purchase_success(
        self,
        test_buyer: User,
        test_car: Car,
        test_dealership: Dealership,
        test_inventory: Inventory,
        test_offer: Offer,
    ) -> None:
        profile = UserProfile.objects.get(user=test_buyer)

        profile.balance = Decimal("50000.00")
        profile.total_spent = Decimal("0.00")
        profile.purchase_count = 0
        profile.save()

        test_offer.refresh_from_db()

        success = execute_offer_purchase(
            test_offer, test_inventory, Decimal("24000.00")
        )

        assert success is True

        test_offer.refresh_from_db()
        assert test_offer.status == OfferStatus.ACCEPTED
        assert test_offer.actual_price == Decimal("24000.00")
        assert test_offer.dealership == test_dealership

        test_inventory.refresh_from_db()
        assert test_inventory.quantity == 4

        profile.refresh_from_db()
        assert profile.balance == Decimal("26000.00")
        assert profile.total_spent == Decimal("24000.00")
        assert profile.purchase_count == 1

    # pylint: disable=unused-argument
    def test_execute_offer_purchase_insufficient_balance(
        self,
        test_buyer: User,
        test_car: Car,
        test_inventory: Inventory,
        test_offer: Offer,
    ) -> None:
        profile = UserProfile.objects.get(user=test_buyer)

        profile.balance = Decimal("10000.00")
        profile.total_spent = Decimal("0.00")
        profile.purchase_count = 0
        profile.save()

        test_offer.refresh_from_db()

        success = execute_offer_purchase(
            test_offer, test_inventory, Decimal("24000.00")
        )

        assert success is False

        test_offer.refresh_from_db()
        assert test_offer.status == OfferStatus.PENDING
        assert test_offer.actual_price is None

        test_inventory.refresh_from_db()
        assert test_inventory.quantity == 5

        profile.refresh_from_db()
        assert profile.balance == Decimal("10000.00")
