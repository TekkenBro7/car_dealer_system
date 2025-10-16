from datetime import timedelta
from decimal import Decimal
from typing import Any, Dict, List

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from cars.models import BodyType, Car, CarBrand
from dealerships.models import (
    Dealership,
    DealershipPromotion,
    DealershipSaleHistory,
    Inventory,
    PreferredModel,
)
from suppliers.models import Supplier, SupplierOffer
from users.models import User


@pytest.fixture
def car_brand() -> CarBrand:
    return CarBrand.objects.create(name="Toyota", country="Japan")


@pytest.fixture
def body_type() -> BodyType:
    return BodyType.objects.create(name="Sedan")


@pytest.fixture
def car(car_brand: CarBrand, body_type: BodyType) -> Car:
    return Car.objects.create(brand=car_brand, body_type=body_type, model_name="Camry")


@pytest.fixture
def car_models(car_brand: CarBrand, body_type: BodyType) -> List[Car]:
    models_data: List[Dict[str, str]] = [
        {"model_name": "Camry"},
        {"model_name": "Corolla"},
        {"model_name": "RAV4"},
        {"model_name": "Highlander"},
    ]
    return [
        Car.objects.create(brand=car_brand, body_type=body_type, **data)
        for data in models_data
    ]


@pytest.fixture
def dealership() -> Dealership:
    return Dealership.objects.create(
        name="City Motors", country="US", city="New York", balance=Decimal("100000.00")
    )


@pytest.fixture
def user() -> User:
    return User.objects.create_user(
        username="test_customer", email="customer@example.com", password="testpass123"
    )


@pytest.fixture
def supplier() -> Supplier:
    return Supplier.objects.create(name="Auto Suppliers Inc", country="US")


@pytest.mark.django_db
class TestDealershipModel:
    def test_dealership_creation(self, dealership: Dealership) -> None:
        assert dealership.name == "City Motors"
        assert dealership.country == "US"
        assert dealership.city == "New York"
        assert dealership.balance == Decimal("100000.00")
        assert dealership.created_at is not None
        assert dealership.updated_at is not None

    def test_dealership_string_representation(self, dealership: Dealership) -> None:
        assert str(dealership) == "City Motors"

    def test_dealership_optional_city(self) -> None:
        dealership = Dealership.objects.create(
            name="Country Dealership", country="DE", balance=Decimal("50000.00")
        )

        assert dealership.city == ""
        assert str(dealership) == "Country Dealership"

    def test_dealership_positive_balance_validation(self) -> None:
        dealership = Dealership(
            name="Valid Dealership", country="US", balance=Decimal("1000.00")
        )
        dealership.full_clean()

        dealership_invalid = Dealership(
            name="Invalid Dealership", country="US", balance=Decimal("0.00")
        )
        with pytest.raises(ValidationError):
            dealership_invalid.full_clean()

        dealership_negative = Dealership(
            name="Negative Dealership", country="US", balance=Decimal("-100.00")
        )
        with pytest.raises(ValidationError):
            dealership_negative.full_clean()


@pytest.mark.django_db
class TestGetBestSuppliersMethod:
    def test_get_best_suppliers_empty(self, dealership: Dealership) -> None:
        result = dealership.get_best_suppliers()

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_get_best_suppliers_single_car_single_supplier(
        self, dealership: Dealership, supplier: Supplier, car: Car
    ) -> None:
        SupplierOffer.objects.create(
            supplier=supplier, car=car, price=Decimal("25000.00"), is_active=True
        )

        result = dealership.get_best_suppliers()

        assert len(result) == 1
        assert car.model_name in result
        assert result[car.model_name]["supplier"] == supplier.name
        assert result[car.model_name]["price"] == Decimal("25000.00")

    def test_get_best_suppliers_multiple_suppliers_same_car(
        self, dealership: Dealership, car: Car
    ) -> None:
        suppliers: List[Supplier] = [
            Supplier.objects.create(name=f"Supplier_{i}", country="US")
            for i in range(3)
        ]

        prices: List[Decimal] = [
            Decimal("25500.00"),
            Decimal("25000.00"),
            Decimal("26000.00"),
        ]
        for supplier, price in zip(suppliers, prices):
            SupplierOffer.objects.create(
                supplier=supplier, car=car, price=price, is_active=True
            )

        result = dealership.get_best_suppliers()

        assert len(result) == 1
        assert result[car.model_name]["price"] == Decimal("25000.00")
        assert result[car.model_name]["supplier"] == "Supplier_1"

    def test_get_best_suppliers_multiple_cars(
        self, dealership: Dealership, supplier: Supplier, car_models: List[Car]
    ) -> None:
        prices: List[Decimal] = [
            Decimal("25000.00"),
            Decimal("22000.00"),
            Decimal("35000.00"),
            Decimal("40000.00"),
        ]
        for car, price in zip(car_models, prices):
            SupplierOffer.objects.create(
                supplier=supplier, car=car, price=price, is_active=True
            )

        result = dealership.get_best_suppliers()
        assert len(result) == 4
        for car in car_models:
            assert car.model_name in result
            assert result[car.model_name]["supplier"] == supplier.name

    def test_get_best_suppliers_excludes_inactive_suppliers(
        self, dealership: Dealership, car: Car
    ) -> None:
        active_supplier: Supplier = Supplier.objects.create(
            name="Active Supplier", country="US"
        )
        SupplierOffer.objects.create(
            supplier=active_supplier, car=car, price=Decimal("25000.00"), is_active=True
        )

        inactive_supplier: Supplier = Supplier.objects.create(
            name="Inactive Supplier", country="US", is_active=False
        )
        SupplierOffer.objects.create(
            supplier=inactive_supplier,
            car=car,
            price=Decimal("20000.00"),
            is_active=True,
        )

        result = dealership.get_best_suppliers()

        assert len(result) == 1
        assert result[car.model_name]["supplier"] == "Active Supplier"
        assert result[car.model_name]["price"] == Decimal("25000.00")

    def test_get_best_suppliers_excludes_inactive_offers(
        self, dealership: Dealership, supplier: Supplier, car: Car
    ) -> None:
        supplier2: Supplier = Supplier.objects.create(
            name="Second Supplier", country="US"
        )

        SupplierOffer.objects.create(
            supplier=supplier, car=car, price=Decimal("25000.00"), is_active=True
        )

        SupplierOffer.objects.create(
            supplier=supplier2, car=car, price=Decimal("20000.00"), is_active=False
        )

        result = dealership.get_best_suppliers()

        assert len(result) == 1
        assert result[car.model_name]["price"] == Decimal("25000.00")
        assert result[car.model_name]["supplier"] == supplier.name


@pytest.mark.django_db
class TestDealershipBuyerMethods:
    @pytest.fixture
    def sales_data(self, dealership: Dealership, car: Car) -> Dict[str, Any]:
        users: List[User] = [
            User.objects.create_user(
                username=f"customer_{i}",
                email=f"customer{i}@example.com",
                password="pass",
            )
            for i in range(3)
        ]

        sales: List[DealershipSaleHistory] = []
        prices: List[Decimal] = [
            Decimal("25000.00"),
            Decimal("30000.00"),
            Decimal("22000.00"),
        ]
        for i, (user_obj, price) in enumerate(zip(users, prices)):
            sale = DealershipSaleHistory.objects.create(
                dealership=dealership, car=car, buyer=user_obj, price=price
            )
            sales.append(sale)

        return {"dealership": dealership, "users": users, "sales": sales}

    def test_get_unique_buyers(self, sales_data: Dict[str, Any]) -> None:
        unique_buyers = sales_data["dealership"].get_unique_buyers()

        assert unique_buyers.count() == 3
        buyer_usernames = [buyer["buyer__username"] for buyer in unique_buyers]
        expected_usernames = ["customer_0", "customer_1", "customer_2"]
        assert set(buyer_usernames) == set(expected_usernames)

    def test_get_buyer_statistics(self, sales_data: Dict[str, Any]) -> None:
        stats = sales_data["dealership"].get_buyer_statistics()

        assert stats.count() == 3

        for stat in stats:
            assert "buyer__username" in stat
            assert "total_purchases" in stat
            assert "total_spent" in stat
            assert "avg_price" in stat

        total_spent_values = [stat["total_spent"] for stat in stats]
        assert total_spent_values == sorted(total_spent_values, reverse=True)

    def test_get_unique_buyers_empty(self, dealership: Dealership) -> None:
        unique_buyers = dealership.get_unique_buyers()
        assert unique_buyers.count() == 0

    def test_get_buyer_statistics_empty(self, dealership: Dealership) -> None:
        stats = dealership.get_buyer_statistics()
        assert stats.count() == 0


@pytest.mark.django_db
class TestInventoryModel:
    def test_inventory_creation(self, dealership: Dealership, car: Car) -> None:
        inventory = Inventory.objects.create(dealership=dealership, car=car, quantity=5)

        assert inventory.dealership == dealership
        assert inventory.car == car
        assert inventory.quantity == 5

    def test_inventory_string_representation(
        self, dealership: Dealership, car: Car
    ) -> None:
        inventory = Inventory.objects.create(dealership=dealership, car=car, quantity=3)

        expected_str = f"{dealership.name}: {car.model_name} (3)"
        assert str(inventory) == expected_str

    def test_inventory_default_quantity(self, dealership: Dealership, car: Car) -> None:
        inventory = Inventory.objects.create(dealership=dealership, car=car)

        assert inventory.quantity == 0

    def test_inventory_negative_quantity(
        self, dealership: Dealership, car: Car
    ) -> None:
        with pytest.raises(IntegrityError):
            Inventory.objects.create(dealership=dealership, car=car, quantity=-1)


@pytest.mark.django_db
class TestPreferredModel:
    def test_preferred_model_creation(self, dealership: Dealership, car: Car) -> None:
        preferred = PreferredModel.objects.create(
            dealership=dealership,
            car=car,
            reason="High customer demand and good profit margin",
        )

        assert preferred.dealership == dealership
        assert preferred.car == car
        assert preferred.reason == "High customer demand and good profit margin"

    def test_preferred_model_string_representation(
        self, dealership: Dealership, car: Car
    ) -> None:
        preferred = PreferredModel.objects.create(
            dealership=dealership, car=car, reason="Test reason"
        )

        expected_str = f"{dealership.name} — {car.model_name}"
        assert str(preferred) == expected_str

    def test_preferred_model_optional_reason(
        self, dealership: Dealership, car: Car
    ) -> None:
        preferred = PreferredModel.objects.create(dealership=dealership, car=car)

        assert preferred.reason == ""
        assert preferred.car == car


@pytest.mark.django_db
class TestDealershipPromotion:
    @pytest.fixture
    def promotion_data(self, dealership: Dealership) -> Dict[str, Any]:
        return {
            "dealership": dealership,
            "title": "Summer Clearance",
            "description": "Big discounts on all models",
            "discount_percent": Decimal("15.00"),
            "start_date": timezone.now() + timedelta(days=1),
            "end_date": timezone.now() + timedelta(days=30),
        }

    def test_dealership_promotion_creation(
        self, promotion_data: Dict[str, Any]
    ) -> None:
        promotion = DealershipPromotion.objects.create(**promotion_data)

        assert promotion.dealership == promotion_data["dealership"]
        assert promotion.title == promotion_data["title"]
        assert promotion.description == promotion_data["description"]
        assert promotion.discount_percent == promotion_data["discount_percent"]
        assert promotion.start_date == promotion_data["start_date"]
        assert promotion.end_date == promotion_data["end_date"]

    def test_dealership_promotion_string_representation(
        self, promotion_data: Dict[str, Any]
    ) -> None:
        promotion = DealershipPromotion.objects.create(**promotion_data)

        expected_str = (
            f"{promotion_data['title']} @ {promotion_data['dealership'].name} "
            f"({promotion_data['discount_percent']}%)"
        )
        assert str(promotion) == expected_str

    def test_dealership_promotion_cars_many_to_many(
        self, promotion_data: Dict[str, Any], car: Car
    ) -> None:
        promotion = DealershipPromotion.objects.create(**promotion_data)
        promotion.cars.add(car)

        assert car in promotion.cars.all()
        assert promotion in car.dealership_promotions.all()  # type: ignore

    def test_dealership_promotion_discount_validation(
        self, dealership: Dealership
    ) -> None:
        promotion = DealershipPromotion(
            dealership=dealership,
            title="Valid Promotion",
            discount_percent=Decimal("25.00"),
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=7),
        )
        promotion.full_clean()

        promotion_invalid = DealershipPromotion(
            dealership=dealership,
            title="Invalid Promotion",
            discount_percent=Decimal("-5.00"),
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=7),
        )
        with pytest.raises(ValidationError):
            promotion_invalid.full_clean()


@pytest.mark.django_db
class TestDealershipSaleHistory:
    @pytest.fixture
    def sale_data(
        self, dealership: Dealership, car: Car, user: User
    ) -> DealershipSaleHistory:
        return DealershipSaleHistory.objects.create(
            dealership=dealership, car=car, buyer=user, price=Decimal("28000.00")
        )

    def test_sale_history_creation(
        self,
        sale_data: DealershipSaleHistory,
        dealership: Dealership,
        car: Car,
        user: User,
    ) -> None:
        assert sale_data.dealership == dealership
        assert sale_data.car == car
        assert sale_data.buyer == user
        assert sale_data.price == Decimal("28000.00")
        assert sale_data.sale_date is not None

    def test_sale_history_string_representation(
        self, sale_data: DealershipSaleHistory
    ) -> None:
        expected_str = (
            f"{sale_data.dealership.name} sold {sale_data.car.model_name} "
            f"to {sale_data.buyer.username}"
        )
        assert str(sale_data) == expected_str

    def test_sale_history_positive_price_validation(
        self,
        sale_data: DealershipSaleHistory,
        dealership: Dealership,
        car: Car,
        user: User,
    ) -> None:
        sale_data.full_clean()

        sale_invalid = DealershipSaleHistory(
            dealership=dealership, car=car, buyer=user, price=Decimal("0.00")
        )
        with pytest.raises(ValidationError):
            sale_invalid.full_clean()

    def test_sale_history_auto_sale_date(
        self,
        sale_data: DealershipSaleHistory,
    ) -> None:
        assert sale_data.sale_date is not None

        time_diff = timezone.now() - sale_data.sale_date
        assert time_diff.total_seconds() < 5
