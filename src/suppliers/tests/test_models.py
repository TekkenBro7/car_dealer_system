from datetime import timedelta
from typing import Any

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from django.utils import timezone

from cars.models import BodyType, Car, CarBrand
from dealerships.models import Dealership
from suppliers.models import (
    Supplier,
    SupplierOffer,
    SupplierPromotion,
    SupplierSaleHistory,
)
from suppliers.validators import validate_positive_value


@pytest.fixture
def supplier() -> Supplier:
    return Supplier.objects.create(
        name="Best Auto Supplies",
        country="US",
        contact_email="contact@bestauto.com",
        description="Leading auto parts supplier",
    )


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
def dealership() -> Dealership:
    return Dealership.objects.create(
        name="City Motors", country="US", city="New York", balance="100000.00"
    )


@pytest.mark.django_db
class TestPositivePriceValidator:
    def test_validate_positive_price_valid(self) -> None:
        validate_positive_value(0.01)
        validate_positive_value(1.00)
        validate_positive_value(1000000.00)

    def test_validate_positive_price_invalid(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_value(0.00)
        assert "greater than 0" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            validate_positive_value(-1.00)
        assert "greater than 0" in str(exc_info.value)


@pytest.mark.django_db
class TestSupplierModel:
    def test_supplier_creation(self, supplier: Supplier) -> None:
        assert supplier.name == "Best Auto Supplies"
        assert supplier.country == "US"
        assert supplier.contact_email == "contact@bestauto.com"
        assert supplier.description == "Leading auto parts supplier"
        assert supplier.founded_year is None
        assert supplier.created_at is not None
        assert supplier.updated_at is not None

    def test_supplier_string_representation(self, supplier: Supplier) -> None:
        assert str(supplier) == "Best Auto Supplies"

    # pylint: disable=unused-argument
    def test_supplier_unique_name(self, supplier: Supplier) -> None:
        with pytest.raises(IntegrityError):
            Supplier.objects.create(name="Best Auto Supplies", country="DE")

    def test_supplier_optional_fields(self) -> None:
        supplier_minimal = Supplier.objects.create(name="Test Supplier", country="RU")

        assert supplier_minimal.name == "Test Supplier"
        assert supplier_minimal.country == "RU"
        assert supplier_minimal.contact_email == ""
        assert supplier_minimal.description == ""
        assert supplier_minimal.founded_year is None

    def test_supplier_with_founded_year(self) -> None:
        supplier = Supplier.objects.create(
            name="Old Supplier", country="DE", founded_year=1990
        )

        assert supplier.founded_year == 1990


@pytest.mark.django_db
class TestSupplierOfferModel:
    @pytest.fixture
    def supplier_offer_data(self, supplier: Supplier, car: Car) -> dict[str, Any]:
        return {"supplier": supplier, "car": car, "price": 25000.00}

    def test_supplier_offer_creation(self, supplier_offer_data: dict[str, Any]) -> None:
        offer = SupplierOffer.objects.create(**supplier_offer_data)

        assert offer.supplier == supplier_offer_data["supplier"]
        assert offer.car == supplier_offer_data["car"]
        assert offer.price == supplier_offer_data["price"]
        assert offer.created_at is not None
        assert offer.updated_at is not None

    def test_supplier_offer_string_representation(
        self, supplier_offer_data: dict[str, Any]
    ) -> None:
        offer = SupplierOffer.objects.create(**supplier_offer_data)

        expected_str = (
            f"{supplier_offer_data['supplier'].name} offers {supplier_offer_data['car']} "
            f"for ${supplier_offer_data['price']}"
        )
        assert str(offer) == expected_str

    def test_supplier_offer_unique_together(
        self, supplier_offer_data: dict[str, Any]
    ) -> None:
        SupplierOffer.objects.create(**supplier_offer_data)

        with pytest.raises(IntegrityError):
            SupplierOffer.objects.create(**supplier_offer_data)

    def test_supplier_offer_different_suppliers_same_car(
        self, supplier: Supplier, car: Car
    ) -> None:
        supplier2 = Supplier.objects.create(name="Second Supplier", country="DE")

        offer1 = SupplierOffer.objects.create(
            supplier=supplier, car=car, price=25000.00
        )
        offer2 = SupplierOffer.objects.create(
            supplier=supplier2, car=car, price=24000.00
        )

        assert offer1.supplier == supplier
        assert offer2.supplier == supplier2
        assert offer1.car == car
        assert offer2.car == car

    def test_supplier_offer_positive_price_validation(
        self, supplier: Supplier, car: Car
    ) -> None:
        offer = SupplierOffer(supplier=supplier, car=car, price=100.00)
        offer.full_clean()

        offer_invalid = SupplierOffer(supplier=supplier, car=car, price=0.00)
        with pytest.raises(ValidationError):
            offer_invalid.full_clean()

    def test_supplier_offer_cascade_delete(
        self, supplier_offer_data: dict[str, Any]
    ) -> None:
        offer = SupplierOffer.objects.create(**supplier_offer_data)
        offer_id = offer.id  # type: ignore

        supplier_offer_data["supplier"].delete()

        with pytest.raises(SupplierOffer.DoesNotExist):
            SupplierOffer.objects.get(id=offer_id)


@pytest.mark.django_db
class TestSupplierPromotionModel:
    @pytest.fixture
    def promotion_data(self, supplier: Supplier) -> dict[str, Any]:
        return {
            "supplier": supplier,
            "title": "Summer Sale",
            "description": "Big summer discounts on all models",
            "discount_percent": 15.00,
            "start_date": timezone.now() + timedelta(days=1),
            "end_date": timezone.now() + timedelta(days=30),
        }

    def test_supplier_promotion_creation(self, promotion_data: dict[str, Any]) -> None:
        promotion = SupplierPromotion.objects.create(**promotion_data)

        assert promotion.supplier == promotion_data["supplier"]
        assert promotion.title == promotion_data["title"]
        assert promotion.description == promotion_data["description"]
        assert promotion.discount_percent == promotion_data["discount_percent"]
        assert promotion.start_date == promotion_data["start_date"]
        assert promotion.end_date == promotion_data["end_date"]
        assert promotion.created_at is not None
        assert promotion.updated_at is not None

    def test_supplier_promotion_string_representation(
        self, promotion_data: dict[str, Any]
    ) -> None:
        promotion = SupplierPromotion.objects.create(**promotion_data)

        expected_str = (
            f"{promotion_data['title']} @ {promotion_data['supplier'].name} "
            f"({promotion_data['discount_percent']}%)"
        )
        assert str(promotion) == expected_str

    def test_supplier_promotion_cars_many_to_many(
        self, promotion_data: dict[str, Any], car: Car
    ) -> None:
        promotion = SupplierPromotion.objects.create(**promotion_data)
        promotion.cars.add(car)

        assert car in promotion.cars.all()
        assert promotion in car.supplier_promotions.all()  # type: ignore

    def test_supplier_promotion_multiple_cars(
        self, promotion_data: dict[str, Any]
    ) -> None:
        brand = CarBrand.objects.create(name="Honda", country="Japan")
        body_type = BodyType.objects.create(name="SUV")
        cars = [
            Car.objects.create(
                brand=brand, body_type=body_type, model_name=f"Model_{i}"
            )
            for i in range(3)
        ]

        promotion = SupplierPromotion.objects.create(**promotion_data)
        promotion.cars.set(cars)

        assert promotion.cars.count() == 3
        for car_obj in cars:
            assert car_obj in promotion.cars.all()


@pytest.mark.django_db
class TestSupplierSaleHistoryModel:
    @pytest.fixture
    def sale_data(
        self, supplier: Supplier, dealership: Dealership, car: Car
    ) -> dict[str, Any]:
        return {
            "supplier": supplier,
            "dealership": dealership,
            "car": car,
            "price": 22000.00,
        }

    def test_supplier_sale_history_creation(self, sale_data: dict[str, Any]) -> None:
        sale = SupplierSaleHistory.objects.create(**sale_data)

        assert sale.supplier == sale_data["supplier"]
        assert sale.dealership == sale_data["dealership"]
        assert sale.car == sale_data["car"]
        assert sale.price == sale_data["price"]
        assert sale.sale_date is not None
        assert sale.created_at is not None
        assert sale.updated_at is not None

    def test_supplier_sale_history_string_representation(
        self, sale_data: dict[str, Any]
    ) -> None:
        sale = SupplierSaleHistory.objects.create(**sale_data)

        expected_str = (
            f"{sale_data['supplier'].name} -> {sale_data['dealership'].name}: "
            f"{sale_data['car']} ${sale_data['price']}"
        )
        assert str(sale) == expected_str

    def test_supplier_sale_history_without_dealership(
        self, supplier: Supplier, car: Car
    ) -> None:
        sale = SupplierSaleHistory.objects.create(
            supplier=supplier, car=car, price=20000.00
        )

        assert sale.supplier == supplier
        assert sale.car == car
        assert sale.dealership is None
        assert "N/A" in str(sale)

    def test_supplier_sale_history_car_protect_on_delete(
        self, sale_data: dict[str, Any]
    ) -> None:
        SupplierSaleHistory.objects.create(**sale_data)

        with pytest.raises(ProtectedError):
            sale_data["car"].delete()

    def test_supplier_sale_history_dealership_set_null(
        self, sale_data: dict[str, Any]
    ) -> None:
        sale = SupplierSaleHistory.objects.create(**sale_data)

        sale_data["dealership"].delete()

        sale.refresh_from_db()

        assert sale.dealership is None

    def test_supplier_sale_history_supplier_cascade_delete(
        self, sale_data: dict[str, Any]
    ) -> None:
        sale = SupplierSaleHistory.objects.create(**sale_data)
        sale_id = sale.id  # type: ignore

        sale_data["supplier"].delete()

        with pytest.raises(SupplierSaleHistory.DoesNotExist):
            SupplierSaleHistory.objects.get(id=sale_id)

    def test_supplier_sale_history_auto_sale_date(
        self, supplier: Supplier, car: Car
    ) -> None:
        sale = SupplierSaleHistory.objects.create(
            supplier=supplier, car=car, price=25000.00
        )

        assert sale.sale_date is not None

        time_diff = timezone.now() - sale.sale_date
        assert time_diff.total_seconds() < 5
