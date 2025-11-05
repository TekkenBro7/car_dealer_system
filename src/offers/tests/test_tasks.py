from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone

from cars.models import BodyType, Car, CarBrand
from dealerships.models import Dealership, Inventory
from offers.models import Offer, OfferStatus
from offers.tasks import process_pending_offers
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
class TestProcessPendingOffers:
    @patch("offers.tasks.apply_dealership_promotion_price")
    def test_successful_offer_processing(
        self,
        mock_apply_promotion: MagicMock,
        test_buyer: User,
        test_car: Car,
        test_dealership: Dealership,
        test_inventory: Inventory,
        test_offer: Offer,
    ) -> None:
        mock_apply_promotion.return_value = Decimal("24000.00")

        profile = UserProfile.objects.get(user=test_buyer)

        profile.balance = Decimal("50000.00")
        profile.total_spent = Decimal("0.00")
        profile.purchase_count = 0
        profile.save()

        process_pending_offers()

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

        mock_apply_promotion.assert_called_once_with(
            test_dealership, test_car, timezone.now().date()
        )

    # pylint: disable=unused-argument
    @patch("offers.tasks.apply_dealership_promotion_price")
    def test_offer_rejected_when_insufficient_balance(
        self,
        mock_apply_promotion: MagicMock,
        test_buyer: User,
        test_car: Car,
        test_inventory: Inventory,
        test_offer: Offer,
    ) -> None:
        mock_apply_promotion.return_value = Decimal("24000.00")

        profile = UserProfile.objects.get(user=test_buyer)

        profile.balance = Decimal("10000.00")
        profile.total_spent = Decimal("0.00")
        profile.purchase_count = 0
        profile.save()

        process_pending_offers()

        test_offer.refresh_from_db()
        assert test_offer.status == OfferStatus.REJECTED
        assert test_offer.actual_price is None
        assert test_offer.dealership is None

        test_inventory.refresh_from_db()
        assert test_inventory.quantity == 5

    # pylint: disable=unused-argument
    @patch("offers.tasks.apply_dealership_promotion_price")
    def test_no_suitable_dealerships_found(
        self,
        mock_apply_promotion: MagicMock,
        test_buyer: User,
        test_car: Car,
        test_offer: Offer,
    ) -> None:
        mock_apply_promotion.return_value = None

        process_pending_offers()

        test_offer.refresh_from_db()
        assert test_offer.status == OfferStatus.PENDING

    # pylint: disable=unused-argument
    @patch("offers.tasks.apply_dealership_promotion_price")
    def test_offer_rejected_when_price_exceeds_max_price(
        self,
        mock_apply_promotion: MagicMock,
        test_buyer: User,
        test_car: Car,
        test_inventory: Inventory,
        test_offer: Offer,
    ) -> None:
        mock_apply_promotion.return_value = Decimal("35000.00")

        process_pending_offers()

        test_offer.refresh_from_db()
        assert test_offer.status == OfferStatus.PENDING

    def test_no_pending_offers(self) -> None:
        process_pending_offers()

        assert Offer.objects.count() == 0

    def test_multiple_dealerships_selects_cheapest(
        self, test_buyer: User, test_car: Car, test_offer: Offer
    ) -> None:
        dealership1 = Dealership.objects.create(
            name="Dealer 1", country="US", city="NY"
        )
        dealership2 = Dealership.objects.create(
            name="Dealer 2", country="US", city="LA"
        )

        Inventory.objects.create(
            dealership=dealership1, car=test_car, quantity=3, price=Decimal("28000.00")
        )
        Inventory.objects.create(
            dealership=dealership2, car=test_car, quantity=2, price=Decimal("26000.00")
        )

        profile = UserProfile.objects.get(user=test_buyer)

        profile.balance = Decimal("50000.00")
        profile.total_spent = Decimal("0.00")
        profile.purchase_count = 0
        profile.save()

        process_pending_offers()

        test_offer.refresh_from_db()
        assert test_offer.status == OfferStatus.ACCEPTED
        assert test_offer.dealership == dealership2
        assert test_offer.actual_price == Decimal("26000.00")
