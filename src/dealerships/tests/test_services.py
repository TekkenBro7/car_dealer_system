from datetime import timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone

from cars.models import BodyType, Car, CarBrand
from dealerships.models import (
    Dealership,
    DealershipSaleHistory,
    Inventory,
    PreferredModel,
)
from dealerships.services.autobuy import (
    _select_best_offer_for_car,
    execute_purchase,
    select_global_best_offer,
    select_history_best_offer,
    select_preferred_best_offer,
)
from dealerships.services.inventory import update_inventory
from dealerships.services.supplier_offers import (
    apply_supplier_promotion_price,
    find_best_offer_for_car,
)
from suppliers.models import Supplier, SupplierOffer, SupplierPromotion
from users.models import User


@pytest.fixture
def test_buyer() -> User:
    return User.objects.create_user(
        username="test_buyer",
        email="buyer@example.com",
        password="testpass123",
        email_confirmed=True,
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
        name="Test Supplier", country="US", founded_year=2000
    )


@pytest.fixture
def test_dealership() -> Dealership:
    return Dealership.objects.create(
        name="Test Dealership",
        country="US",
        city="New York",
        balance=Decimal("100000.00"),
    )


@pytest.mark.django_db
class TestAutoBuyServices:
    @patch("dealerships.services.autobuy.find_best_offer_for_car")
    def test_select_best_offer_for_car_success(
        self, mock_find_offer: MagicMock, test_car: Car, test_supplier: Supplier
    ) -> None:
        supplier_offer = SupplierOffer(
            supplier=test_supplier, car=test_car, price=Decimal("25000.00")
        )
        mock_find_offer.return_value = (supplier_offer, Decimal("25000.00"))

        offer, price, car = _select_best_offer_for_car(test_car, timezone.now().date())

        assert offer == supplier_offer
        assert price == Decimal("25000.00")
        assert car == test_car

    @patch("dealerships.services.autobuy.find_best_offer_for_car")
    def test_select_best_offer_for_car_no_offer(
        self, mock_find_offer: MagicMock, test_car: Car
    ) -> None:
        mock_find_offer.return_value = (None, None)

        offer, price, car = _select_best_offer_for_car(test_car, timezone.now().date())

        assert offer is None
        assert price is None
        assert car is None

    @patch("dealerships.services.autobuy._select_best_offer_for_car")
    def test_select_preferred_best_offer(
        self,
        mock_select_offer: MagicMock,
        test_dealership: Dealership,
        test_car: Car,
        test_car2: Car,
        test_supplier: Supplier,
    ) -> None:
        PreferredModel.objects.create(
            dealership=test_dealership, car=test_car, reason="Popular"
        )
        PreferredModel.objects.create(
            dealership=test_dealership, car=test_car2, reason="Economical"
        )

        mock_select_offer.side_effect = [
            (test_supplier, Decimal("28000.00"), test_car),
            (test_supplier, Decimal("22000.00"), test_car2),
        ]

        _, price, car = select_preferred_best_offer(
            test_dealership, timezone.now().date()
        )

        assert price == Decimal("22000.00")
        assert car == test_car2

    @patch("dealerships.services.autobuy._select_best_offer_for_car")
    def test_select_preferred_best_offer_no_affordable(
        self,
        mock_select_offer: MagicMock,
        test_dealership: Dealership,
        test_car: Car,
        test_supplier: Supplier,
    ) -> None:
        PreferredModel.objects.create(
            dealership=test_dealership, car=test_car, reason="Popular"
        )

        mock_select_offer.return_value = (test_supplier, Decimal("150000.00"), test_car)

        offer, price, car = select_preferred_best_offer(
            test_dealership, timezone.now().date()
        )

        assert offer is None
        assert price is None
        assert car is None

    @patch("dealerships.services.autobuy._select_best_offer_for_car")
    def test_select_history_best_offer(
        self,
        mock_select: MagicMock,
        test_dealership: Dealership,
        test_car: Car,
        test_car2: Car,
        test_buyer: User,
    ) -> None:
        DealershipSaleHistory.objects.create(
            dealership=test_dealership,
            car=test_car,
            buyer=test_buyer,
            price=Decimal("30000.00"),
        )
        for _ in range(3):
            DealershipSaleHistory.objects.create(
                dealership=test_dealership,
                car=test_car2,
                buyer=test_buyer,
                price=Decimal("25000.00"),
            )

        mock_select.return_value = (None, Decimal("20000.00"), test_car2)

        _, _, car = select_history_best_offer(test_dealership, timezone.now().date())

        assert car == test_car2

    def test_select_history_best_offer_no_history(
        self, test_dealership: Dealership
    ) -> None:
        offer, price, car = select_history_best_offer(
            test_dealership, timezone.now().date()
        )

        assert offer is None
        assert price is None
        assert car is None

    @patch("dealerships.services.autobuy._select_best_offer_for_car")
    def test_select_global_best_offer(
        self, mock_select: MagicMock, test_car: Car, test_car2: Car, test_buyer: User
    ) -> None:
        dealership1 = Dealership.objects.create(
            name="Dealer 1", country="US", city="NY"
        )
        dealership2 = Dealership.objects.create(
            name="Dealer 2", country="US", city="LA"
        )

        DealershipSaleHistory.objects.create(
            dealership=dealership1,
            car=test_car,
            buyer=test_buyer,
            price=Decimal("30000.00"),
        )
        for _ in range(2):
            DealershipSaleHistory.objects.create(
                dealership=dealership2,
                car=test_car2,
                buyer=test_buyer,
                price=Decimal("25000.00"),
            )

        mock_select.return_value = (None, Decimal("22000.00"), test_car2)

        _, _, car = select_global_best_offer(timezone.now().date())

        assert car == test_car2

    def test_execute_purchase(self, test_dealership: Dealership, test_car: Car) -> None:
        initial_balance = test_dealership.balance
        purchase_price = Decimal("25000.00")

        execute_purchase(test_dealership, test_car, purchase_price)

        test_dealership.refresh_from_db()
        assert test_dealership.balance == initial_balance - purchase_price

        inventory = Inventory.objects.get(dealership=test_dealership, car=test_car)
        assert inventory.quantity == 1
        assert inventory.price == purchase_price


@pytest.mark.django_db
class TestInventoryService:
    def test_update_inventory_create_new(
        self, test_dealership: Dealership, test_car: Car
    ) -> None:
        assert not Inventory.objects.filter(
            dealership=test_dealership, car=test_car
        ).exists()

        update_inventory(test_dealership, test_car, Decimal("25000.00"))

        inventory = Inventory.objects.get(dealership=test_dealership, car=test_car)
        assert inventory.quantity == 1
        assert inventory.price == Decimal("25000")
        assert inventory.is_active is True

    def test_update_inventory_increase_existing(
        self, test_dealership: Dealership, test_car: Car
    ) -> None:
        Inventory.objects.create(
            dealership=test_dealership,
            car=test_car,
            quantity=3,
            price=Decimal("30000.00"),
        )

        update_inventory(test_dealership, test_car, Decimal("25000.00"))

        inventory = Inventory.objects.get(dealership=test_dealership, car=test_car)
        assert inventory.quantity == 4
        assert inventory.price == Decimal("25000.00")

    def test_update_inventory_multiple_purchases_same_car(
        self, test_dealership: Dealership, test_car: Car
    ) -> None:
        update_inventory(test_dealership, test_car, Decimal("25000.00"))

        update_inventory(test_dealership, test_car, Decimal("23000.00"))

        update_inventory(test_dealership, test_car, Decimal("24000.00"))

        inventory = Inventory.objects.get(dealership=test_dealership, car=test_car)
        assert inventory.quantity == 3
        assert inventory.price == Decimal("24000.00")


@pytest.mark.django_db
class TestSupplierOffersServices:
    def test_apply_supplier_promotion_price_no_promotions(
        self, test_supplier: Supplier, test_car: Car
    ) -> None:
        offer = SupplierOffer.objects.create(
            supplier=test_supplier, car=test_car, price=Decimal("25000.00")
        )

        result = apply_supplier_promotion_price(offer, timezone.now().date())

        assert result == Decimal("25000.00")

    def test_apply_supplier_promotion_price_with_global_promotion(
        self, test_supplier: Supplier, test_car: Car
    ) -> None:
        offer = SupplierOffer.objects.create(
            supplier=test_supplier, car=test_car, price=Decimal("25000.00")
        )

        SupplierPromotion.objects.create(
            supplier=test_supplier,
            title="Summer Sale",
            discount_percent=Decimal("15.00"),
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
        )

        result = apply_supplier_promotion_price(offer, timezone.now().date())

        assert result == Decimal("21250.00")

    def test_apply_supplier_promotion_price_with_specific_car_promotion(
        self, test_supplier: Supplier, test_car: Car
    ) -> None:
        """Тест расчета цены с акцией для конкретного автомобиля"""
        offer = SupplierOffer.objects.create(
            supplier=test_supplier, car=test_car, price=Decimal("25000.00")
        )

        promotion = SupplierPromotion.objects.create(
            supplier=test_supplier,
            title="Camry Special",
            discount_percent=Decimal("20.00"),
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
        )
        promotion.cars.add(test_car)

        result = apply_supplier_promotion_price(offer, timezone.now().date())

        assert result == Decimal("20000.00")

    def test_apply_supplier_promotion_price_multiple_promotions(
        self, test_supplier: Supplier, test_car: Car
    ) -> None:
        offer = SupplierOffer.objects.create(
            supplier=test_supplier, car=test_car, price=Decimal("25000.00")
        )

        SupplierPromotion.objects.create(
            supplier=test_supplier,
            title="Global Sale",
            discount_percent=Decimal("10.00"),
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
        )

        promotion = SupplierPromotion.objects.create(
            supplier=test_supplier,
            title="Specific Sale",
            discount_percent=Decimal("15.00"),
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
        )
        promotion.cars.add(test_car)

        result = apply_supplier_promotion_price(offer, timezone.now().date())

        assert result == Decimal("18750.00")

    def test_apply_supplier_promotion_price_discount_capped_at_100(
        self, test_supplier: Supplier, test_car: Car
    ) -> None:
        offer = SupplierOffer.objects.create(
            supplier=test_supplier, car=test_car, price=Decimal("25000.00")
        )

        SupplierPromotion.objects.create(
            supplier=test_supplier,
            title="Huge Discount",
            discount_percent=Decimal("80.00"),
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
        )

        promotion = SupplierPromotion.objects.create(
            supplier=test_supplier,
            title="Another Discount",
            discount_percent=Decimal("50.00"),
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
        )
        promotion.cars.add(test_car)

        result = apply_supplier_promotion_price(offer, timezone.now().date())

        assert result == Decimal("0.00")

    def test_apply_supplier_promotion_price_expired_promotion(
        self, test_supplier: Supplier, test_car: Car
    ) -> None:
        offer = SupplierOffer.objects.create(
            supplier=test_supplier, car=test_car, price=Decimal("25000.00")
        )

        SupplierPromotion.objects.create(
            supplier=test_supplier,
            title="Expired Sale",
            discount_percent=Decimal("20.00"),
            start_date=timezone.now().date() - timedelta(days=60),
            end_date=timezone.now().date() - timedelta(days=30),
        )

        result = apply_supplier_promotion_price(offer, timezone.now().date())

        assert result == Decimal("25000.00")

    def test_find_best_offer_for_car_single_offer(
        self, test_supplier: Supplier, test_car: Car
    ) -> None:
        SupplierOffer.objects.create(
            supplier=test_supplier, car=test_car, price=Decimal("25000.00")
        )

        offer, price = find_best_offer_for_car(test_car, timezone.now().date())
        assert offer is not None
        assert offer.supplier == test_supplier
        assert price == Decimal("25000.00")

    def test_find_best_offer_for_car_multiple_suppliers(self, test_car: Car) -> None:
        supplier1 = Supplier.objects.create(name="Supplier 1", country="US")
        supplier2 = Supplier.objects.create(name="Supplier 2", country="JP")
        supplier3 = Supplier.objects.create(name="Supplier 3", country="DE")

        SupplierOffer.objects.create(
            supplier=supplier1, car=test_car, price=Decimal("28000.00")
        )
        SupplierOffer.objects.create(
            supplier=supplier2, car=test_car, price=Decimal("26000.00")
        )
        SupplierOffer.objects.create(
            supplier=supplier3, car=test_car, price=Decimal("27000.00")
        )

        offer, price = find_best_offer_for_car(test_car, timezone.now().date())

        assert offer is not None
        assert offer.supplier == supplier2
        assert price == Decimal("26000.00")

    def test_find_best_offer_for_car_with_promotions(self, test_car: Car) -> None:
        supplier1 = Supplier.objects.create(name="Supplier 1", country="US")
        supplier2 = Supplier.objects.create(name="Supplier 2", country="JP")

        SupplierOffer.objects.create(
            supplier=supplier1, car=test_car, price=Decimal("30000.00")
        )
        SupplierPromotion.objects.create(
            supplier=supplier1,
            title="Big Sale",
            discount_percent=Decimal("20.00"),
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
        )

        SupplierOffer.objects.create(
            supplier=supplier2, car=test_car, price=Decimal("25000.00")
        )

        offer, price = find_best_offer_for_car(test_car, timezone.now().date())

        assert offer is not None
        assert offer.supplier == supplier1
        assert price == Decimal("24000.00")

    def test_find_best_offer_for_car_no_offers(self, test_car: Car) -> None:
        offer, _ = find_best_offer_for_car(test_car, timezone.now().date())

        assert offer is None
