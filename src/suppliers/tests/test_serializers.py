from datetime import date
from typing import Any

import pytest

from cars.models import BodyType, Car, CarBrand
from dealerships.models import Dealership
from suppliers.models import (
    Supplier,
    SupplierOffer,
    SupplierPromotion,
    SupplierSaleHistory,
)
from suppliers.serializers import (
    SupplierOfferDetailSerializer,
    SupplierOfferListSerializer,
    SupplierPromotionDetailSerializer,
    SupplierPromotionListSerializer,
    SupplierSaleHistoryDetailSerializer,
    SupplierSaleHistoryListSerializer,
    SupplierSerializer,
)


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
def dealership() -> Dealership:
    return Dealership.objects.create(
        name="Test Dealership", country="US", balance=100000.00
    )


@pytest.fixture
def supplier() -> Supplier:
    return Supplier.objects.create(
        name="Test Supplier",
        founded_year=1990,
        country="US",
        contact_email="supplier@test.com",
        description="Test supplier description",
    )


@pytest.fixture
def supplier_offer(supplier: Supplier, car: Car) -> SupplierOffer:
    return SupplierOffer.objects.create(supplier=supplier, car=car, price=25000.00)


@pytest.fixture
def supplier_promotion(supplier: Supplier, car: Car) -> SupplierPromotion:
    promotion: SupplierPromotion = SupplierPromotion.objects.create(
        supplier=supplier,
        title="Summer Sale",
        description="Big summer discounts",
        discount_percent=15.00,
        start_date=date(2024, 6, 1),
        end_date=date(2024, 8, 31),
    )
    promotion.cars.add(car)
    return promotion


@pytest.fixture
def supplier_sale_history(
    supplier: Supplier, car: Car, dealership: Dealership
) -> SupplierSaleHistory:
    return SupplierSaleHistory.objects.create(
        supplier=supplier, dealership=dealership, car=car, price=23000.00
    )


@pytest.mark.django_db
class TestSupplierSerializer:
    @pytest.fixture
    def valid_data(self) -> dict[str, Any]:
        return {
            "name": "New Supplier",
            "founded_year": 2000,
            "country": "DE",
            "contact_email": "new@supplier.com",
            "description": "New supplier description",
        }

    def test_valid_serializer_data(self, valid_data: dict[str, Any]) -> None:
        serializer = SupplierSerializer(data=valid_data)
        assert serializer.is_valid()

    def test_required_fields(self, valid_data: dict[str, Any]) -> None:
        required_fields = ["name", "country"]

        for field in required_fields:
            invalid_data = valid_data.copy()
            del invalid_data[field]

            serializer = SupplierSerializer(data=invalid_data)
            assert not serializer.is_valid()
            assert field in serializer.errors

    def test_unique_name_validation(
        self, valid_data: dict[str, Any], supplier: Supplier
    ) -> None:
        valid_data["name"] = supplier.name

        serializer = SupplierSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert "name" in serializer.errors

    def test_founded_year_validation(self, valid_data: dict[str, Any]) -> None:
        invalid_data: dict[str, Any] = valid_data.copy()
        invalid_data["founded_year"] = 2050

        serializer = SupplierSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert "founded_year" in serializer.errors

        valid_data["founded_year"] = 2020
        serializer = SupplierSerializer(data=valid_data)
        assert serializer.is_valid()

    def test_country_validation(self, valid_data: dict[str, Any]) -> None:
        invalid_data: dict[str, Any] = valid_data.copy()
        invalid_data["country"] = "INVALID"

        serializer: SupplierSerializer = SupplierSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert "country" in serializer.errors

    def test_create_supplier(self, valid_data: dict[str, Any]) -> None:
        serializer = SupplierSerializer(data=valid_data)
        assert serializer.is_valid()

        supplier: Supplier = serializer.save()
        assert supplier.name == "New Supplier"
        assert supplier.founded_year == 2000
        assert supplier.country == "DE"
        assert supplier.is_active is True

    def test_update_supplier(
        self, supplier: Supplier, valid_data: dict[str, Any]
    ) -> None:
        valid_data["name"] = "Updated Supplier"

        serializer = SupplierSerializer(
            instance=supplier, data=valid_data, partial=True
        )
        assert serializer.is_valid()

        updated_supplier: Supplier = serializer.save()
        assert updated_supplier.name == "Updated Supplier"

    def test_serializer_fields(self, supplier: Supplier) -> None:
        serializer = SupplierSerializer(instance=supplier)

        expected_fields = {
            "id",
            "name",
            "founded_year",
            "country",
            "contact_email",
            "description",
            "created_at",
            "updated_at",
            "is_active",
        }

        assert serializer.data.keys() == expected_fields


@pytest.mark.django_db
class TestSupplierOfferListSerializer:
    @pytest.fixture
    def valid_data(self, supplier: Supplier, car: Car) -> dict[str, Any]:
        return {
            "supplier": supplier.id,
            "car": car.id,
            "price": 30000.00,
        }

    def test_valid_serializer_data(self, valid_data: dict[str, Any]) -> None:
        serializer = SupplierOfferListSerializer(data=valid_data)
        assert serializer.is_valid()

    def test_required_fields(self, valid_data: dict[str, Any]) -> None:
        required_fields = ["supplier", "car", "price"]

        for field in required_fields:
            invalid_data = valid_data.copy()
            del invalid_data[field]

            serializer = SupplierOfferListSerializer(data=invalid_data)
            assert not serializer.is_valid()
            assert field in serializer.errors

    def test_price_validation(self, valid_data: dict[str, Any]) -> None:
        invalid_data = valid_data.copy()
        invalid_data["price"] = -100.00

        serializer = SupplierOfferListSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert "price" in serializer.errors

        invalid_data["price"] = 0.00
        serializer = SupplierOfferListSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert "price" in serializer.errors

    def test_unique_together_validation(
        self, valid_data: dict[str, Any], supplier_offer: SupplierOffer
    ) -> None:
        valid_data["supplier"] = supplier_offer.supplier.id
        valid_data["car"] = supplier_offer.car.id

        serializer = SupplierOfferListSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors

    def test_create_supplier_offer(
        self, valid_data: dict[str, Any], supplier: Supplier, car: Car
    ) -> None:
        serializer = SupplierOfferListSerializer(data=valid_data)
        assert serializer.is_valid()

        offer = serializer.save()
        assert offer.supplier == supplier
        assert offer.car == car
        assert offer.price == 30000.00
        assert offer.is_active is True


@pytest.mark.django_db
class TestSupplierOfferDetailSerializer:
    def test_serializer_fields(self, supplier_offer: SupplierOffer) -> None:
        serializer = SupplierOfferDetailSerializer(instance=supplier_offer)

        expected_fields = {
            "id",
            "supplier",
            "car",
            "price",
            "created_at",
            "updated_at",
            "is_active",
        }

        assert serializer.data.keys() == expected_fields

    def test_nested_serializers(self, supplier_offer: SupplierOffer) -> None:
        serializer = SupplierOfferDetailSerializer(instance=supplier_offer)

        assert isinstance(serializer.data["supplier"], dict)
        assert isinstance(serializer.data["car"], dict)

        assert serializer.data["supplier"]["name"] == supplier_offer.supplier.name
        assert "model_name" in serializer.data["car"]


@pytest.mark.django_db
class TestSupplierPromotionListSerializer:
    @pytest.fixture
    def valid_data(self, supplier: Supplier, car: Car) -> dict[str, Any]:
        return {
            "supplier": supplier.id,
            "title": "Winter Sale",
            "discount_percent": 20.00,
            "start_date": "2024-12-01",
            "end_date": "2024-12-31",
            "cars": [car.id],
        }

    def test_valid_serializer_data(self, valid_data: dict[str, Any]) -> None:
        serializer = SupplierPromotionListSerializer(data=valid_data)
        assert serializer.is_valid()

    def test_required_fields(self, valid_data: dict[str, Any]) -> None:
        required_fields = ["supplier", "title", "start_date", "end_date"]

        for field in required_fields:
            invalid_data = valid_data.copy()
            del invalid_data[field]

            serializer = SupplierPromotionListSerializer(data=invalid_data)
            assert not serializer.is_valid()
            assert field in serializer.errors

    def test_discount_percent_validation(self, valid_data: dict[str, Any]) -> None:
        invalid_data = valid_data.copy()
        invalid_data["discount_percent"] = -10.00

        serializer = SupplierPromotionListSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert "discount_percent" in serializer.errors

        invalid_data["discount_percent"] = 150.00
        serializer = SupplierPromotionListSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert "discount_percent" in serializer.errors

        valid_data["discount_percent"] = 25.50
        serializer = SupplierPromotionListSerializer(data=valid_data)
        assert serializer.is_valid()

    def test_date_validation(self, valid_data: dict[str, Any]) -> None:
        invalid_data: dict[str, Any] = valid_data.copy()
        invalid_data["start_date"] = "2024-12-31"
        invalid_data["end_date"] = "2024-12-01"

        serializer: SupplierPromotionListSerializer = SupplierPromotionListSerializer(
            data=invalid_data
        )
        assert not serializer.is_valid()
        assert "error" in serializer.errors

    def test_create_supplier_promotion(
        self, valid_data: dict[str, Any], supplier: Supplier, car: Car
    ) -> None:
        serializer: SupplierPromotionListSerializer = SupplierPromotionListSerializer(
            data=valid_data
        )
        assert serializer.is_valid()

        promotion: SupplierPromotion = serializer.save()
        assert promotion.title == "Winter Sale"
        assert promotion.discount_percent == 20.00
        assert promotion.supplier == supplier
        assert car in promotion.cars.all()


@pytest.mark.django_db
class TestSupplierPromotionDetailSerializer:
    def test_serializer_fields(self, supplier_promotion: SupplierPromotion) -> None:
        serializer = SupplierPromotionDetailSerializer(instance=supplier_promotion)

        expected_fields = {
            "id",
            "supplier",
            "title",
            "description",
            "cars",
            "discount_percent",
            "start_date",
            "end_date",
            "created_at",
            "updated_at",
            "is_active",
        }

        assert serializer.data.keys() == expected_fields

    def test_nested_serializers(self, supplier_promotion: SupplierPromotion) -> None:
        serializer = SupplierPromotionDetailSerializer(instance=supplier_promotion)

        assert isinstance(serializer.data["supplier"], dict)
        assert isinstance(serializer.data["cars"], list)

        assert serializer.data["supplier"]["name"] == supplier_promotion.supplier.name
        assert len(serializer.data["cars"]) == 1
        assert "model_name" in serializer.data["cars"][0]


@pytest.mark.django_db
class TestSupplierSaleHistoryListSerializer:
    @pytest.fixture
    def valid_data(
        self, supplier: Supplier, car: Car, dealership: Dealership
    ) -> dict[str, Any]:
        return {
            "supplier": supplier.id,
            "dealership": dealership.id,
            "car": car.id,
            "price": 27000.00,
        }

    def test_valid_serializer_data(self, valid_data: dict[str, Any]) -> None:
        serializer = SupplierSaleHistoryListSerializer(data=valid_data)
        assert serializer.is_valid()

    def test_required_fields(self, valid_data: dict[str, Any]) -> None:
        required_fields = ["supplier", "car", "price"]

        for field in required_fields:
            invalid_data = valid_data.copy()
            del invalid_data[field]

            serializer = SupplierSaleHistoryListSerializer(data=invalid_data)
            assert not serializer.is_valid()
            assert field in serializer.errors

    def test_price_validation(self, valid_data: dict[str, Any]) -> None:
        invalid_data = valid_data.copy()
        invalid_data["price"] = -100.00

        serializer = SupplierSaleHistoryListSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert "price" in serializer.errors

    def test_create_supplier_sale_history(
        self,
        valid_data: dict[str, Any],
        supplier: Supplier,
        car: Car,
        dealership: Dealership,
    ) -> None:
        serializer = SupplierSaleHistoryListSerializer(data=valid_data)
        assert serializer.is_valid()

        sale_history = serializer.save()
        assert sale_history.supplier == supplier
        assert sale_history.car == car
        assert sale_history.dealership == dealership
        assert sale_history.price == 27000.00
        assert sale_history.is_active is True


@pytest.mark.django_db
class TestSupplierSaleHistoryDetailSerializer:
    def test_serializer_fields(
        self, supplier_sale_history: SupplierSaleHistory
    ) -> None:
        serializer = SupplierSaleHistoryDetailSerializer(instance=supplier_sale_history)

        expected_fields = {
            "id",
            "supplier",
            "dealership",
            "car",
            "price",
            "sale_date",
            "created_at",
            "updated_at",
            "is_active",
        }

        assert serializer.data.keys() == expected_fields

    def test_nested_serializers(
        self, supplier_sale_history: SupplierSaleHistory
    ) -> None:
        serializer = SupplierSaleHistoryDetailSerializer(instance=supplier_sale_history)

        assert isinstance(serializer.data["supplier"], dict)
        assert isinstance(serializer.data["car"], dict)

        assert (
            serializer.data["supplier"]["name"] == supplier_sale_history.supplier.name
        )
        assert "model_name" in serializer.data["car"]
