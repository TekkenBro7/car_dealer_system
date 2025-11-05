from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone

from cars.models import BodyType, Car, CarBrand
from dealerships.models import (
    Dealership,
    Inventory,
    PreferredModel,
)
from dealerships.tasks import auto_buy_from_suppliers
from suppliers.models import Supplier, SupplierOffer
from users.models import User


@pytest.fixture
def test_buyer() -> User:
    return User.objects.create_user(
        username="test_buyer", email="buyer@example.com", password="testpass123"
    )


@pytest.fixture
def test_car_brand() -> CarBrand:
    return CarBrand.objects.create(name="Toyota", country="JP")


@pytest.fixture
def test_body_type() -> BodyType:
    return BodyType.objects.create(name="Sedan")


@pytest.fixture
def test_car(test_car_brand: CarBrand, test_body_type: BodyType) -> Car:
    return Car.objects.create(
        brand=test_car_brand, body_type=test_body_type, model_name="Camry"
    )


@pytest.fixture
def test_car2(test_car_brand: CarBrand, test_body_type: BodyType) -> Car:
    return Car.objects.create(
        brand=test_car_brand, body_type=test_body_type, model_name="Corolla"
    )


@pytest.fixture
def test_supplier() -> Supplier:
    return Supplier.objects.create(
        name="Test Supplier",
        country="US",
        founded_year=2000,
        contact_email="supplier@example.com",
    )


@pytest.fixture
def test_dealership() -> Dealership:
    return Dealership.objects.create(
        name="Test Dealership",
        country="US",
        city="New York",
        balance=Decimal("100000.00"),
    )


@pytest.fixture
def test_dealership_low_balance() -> Dealership:
    return Dealership.objects.create(
        name="Low Balance Dealership",
        country="US",
        city="Chicago",
        balance=Decimal("10000.00"),
    )


@pytest.fixture
def test_supplier_offer(test_supplier: Supplier, test_car: Car) -> SupplierOffer:
    return SupplierOffer.objects.create(
        supplier=test_supplier, car=test_car, price=Decimal("25000.00")
    )


@pytest.fixture
def test_supplier_offer2(test_supplier: Supplier, test_car2: Car) -> SupplierOffer:
    return SupplierOffer.objects.create(
        supplier=test_supplier, car=test_car2, price=Decimal("20000.00")
    )


@pytest.fixture
def test_preferred_model(test_dealership: Dealership, test_car: Car) -> PreferredModel:
    return PreferredModel.objects.create(
        dealership=test_dealership, car=test_car, reason="Popular model"
    )


@pytest.mark.django_db
class TestAutoBuyFromSuppliers:
    @patch("dealerships.tasks.select_preferred_best_offer")
    @patch("dealerships.tasks.select_history_best_offer")
    @patch("dealerships.tasks.select_global_best_offer")
    def test_successful_purchase_from_preferred_models(
        self,
        mock_global: MagicMock,
        mock_history: MagicMock,
        mock_preferred: MagicMock,
        test_dealership: Dealership,
        test_car: Car,
        test_supplier: Supplier,
    ) -> None:
        mock_preferred.return_value = (test_supplier, Decimal("25000.00"), test_car)
        mock_history.return_value = (None, None, None)
        mock_global.return_value = (None, None, None)

        auto_buy_from_suppliers()

        mock_preferred.assert_called_once_with(test_dealership, timezone.now().date())
        mock_history.assert_not_called()
        mock_global.assert_not_called()

        test_dealership.refresh_from_db()
        assert test_dealership.balance == Decimal("75000.00")

        inventory = Inventory.objects.get(dealership=test_dealership, car=test_car)
        assert inventory.quantity == 1
        assert inventory.price == Decimal("25000.00")

    @patch("dealerships.tasks.select_preferred_best_offer")
    @patch("dealerships.tasks.select_history_best_offer")
    @patch("dealerships.tasks.select_global_best_offer")
    def test_fallback_to_history_strategy(
        self,
        mock_global: MagicMock,
        mock_history: MagicMock,
        mock_preferred: MagicMock,
        test_dealership: Dealership,
        test_car: Car,
        test_supplier: Supplier,
    ) -> None:
        mock_preferred.return_value = (None, None, None)
        mock_history.return_value = (test_supplier, Decimal("20000.00"), test_car)
        mock_global.return_value = (None, None, None)

        auto_buy_from_suppliers()

        mock_preferred.assert_called_once()
        mock_history.assert_called_once_with(test_dealership, timezone.now().date())
        mock_global.assert_not_called()

        test_dealership.refresh_from_db()
        assert test_dealership.balance == Decimal("80000.00")

    @patch("dealerships.tasks.select_preferred_best_offer")
    @patch("dealerships.tasks.select_history_best_offer")
    @patch("dealerships.tasks.select_global_best_offer")
    def test_fallback_to_global_strategy(
        self,
        mock_global: MagicMock,
        mock_history: MagicMock,
        mock_preferred: MagicMock,
        test_dealership: Dealership,
        test_car: Car,
        test_supplier: Supplier,
        test_buyer: User,
    ) -> None:
        mock_preferred.return_value = (None, None, None)
        mock_history.return_value = (None, None, None)
        mock_global.return_value = (test_supplier, Decimal("18000.00"), test_car)

        auto_buy_from_suppliers()

        mock_preferred.assert_called_once()
        mock_history.assert_called_once()
        mock_global.assert_called_once_with(timezone.now().date())

        test_dealership.refresh_from_db()
        assert test_dealership.balance == Decimal("82000.00")

    @patch("dealerships.tasks.select_preferred_best_offer")
    def test_no_purchase_when_insufficient_balance(
        self,
        mock_preferred: MagicMock,
        test_dealership_low_balance: Dealership,
        test_car: Car,
        test_supplier: Supplier,
    ) -> None:
        mock_preferred.return_value = (test_supplier, Decimal("25000.00"), test_car)

        auto_buy_from_suppliers()

        test_dealership_low_balance.refresh_from_db()
        assert test_dealership_low_balance.balance == Decimal("10000.00")

        assert not Inventory.objects.filter(
            dealership=test_dealership_low_balance, car=test_car
        ).exists()

    @patch("dealerships.tasks.select_preferred_best_offer")
    @patch("dealerships.tasks.select_history_best_offer")
    @patch("dealerships.tasks.select_global_best_offer")
    def test_no_offers_found(
        self,
        mock_global: MagicMock,
        mock_history: MagicMock,
        mock_preferred: MagicMock,
        test_dealership: Dealership,
    ) -> None:
        mock_preferred.return_value = (None, None, None)
        mock_history.return_value = (None, None, None)
        mock_global.return_value = (None, None, None)

        auto_buy_from_suppliers()

        mock_preferred.assert_called_once()
        mock_history.assert_called_once()
        mock_global.assert_called_once()

        test_dealership.refresh_from_db()
        assert test_dealership.balance == Decimal("100000.00")

    @patch("dealerships.tasks.select_preferred_best_offer")
    @patch("dealerships.tasks.select_history_best_offer")
    @patch("dealerships.tasks.select_global_best_offer")
    def test_multiple_dealerships_processing(
        self,
        mock_global: MagicMock,
        mock_history: MagicMock,
        mock_preferred: MagicMock,
        test_dealership: Dealership,
        test_car: Car,
        test_supplier: Supplier,
    ) -> None:
        dealership2 = Dealership.objects.create(
            name="Second Dealership",
            country="US",
            city="Chicago",
            balance=Decimal("80000.00"),
        )

        mock_preferred.side_effect = [
            (test_supplier, Decimal("25000.00"), test_car),
            (None, None, None),
        ]
        mock_history.return_value = (test_supplier, Decimal("22000.00"), test_car)
        mock_global.return_value = (None, None, None)

        auto_buy_from_suppliers()

        assert mock_preferred.call_count == 2
        assert mock_history.call_count == 1

        test_dealership.refresh_from_db()
        dealership2.refresh_from_db()
        assert test_dealership.balance == Decimal("75000.00")
        assert dealership2.balance == Decimal("58000.00")
