from datetime import date
from typing import Any

import pytest

from cars.models import BodyType, Car, CarBrand
from dealerships.models import (
    Dealership,
    DealershipPromotion,
    DealershipSaleHistory,
    Inventory,
    PreferredModel,
)
from dealerships.serializers import (
    DealershipPromotionDetailSerializer,
    DealershipPromotionListSerializer,
    DealershipReportSerializer,
    DealershipSaleHistoryDetailSerializer,
    DealershipSaleHistoryListSerializer,
    DealershipSerializer,
    InventoryDetailSerializer,
    InventoryListSerializer,
    PreferredModelDetailSerializer,
    PreferredModelListSerializer,
)
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
def dealership() -> Dealership:
    return Dealership.objects.create(
        name="Test Dealership", country="US", city="New York", balance=100000.00
    )


@pytest.fixture
def inventory(dealership: Dealership, car: Car) -> Inventory:
    return Inventory.objects.create(dealership=dealership, car=car, quantity=5)


@pytest.fixture
def preferred_model(dealership: Dealership, car: Car) -> PreferredModel:
    return PreferredModel.objects.create(
        dealership=dealership, car=car, reason="High demand model"
    )


@pytest.fixture
def dealership_promotion(dealership: Dealership, car: Car) -> DealershipPromotion:
    promotion = DealershipPromotion.objects.create(
        dealership=dealership,
        title="Summer Sale",
        description="Big summer discounts",
        discount_percent=15.00,
        start_date=date(2024, 6, 1),
        end_date=date(2024, 8, 31),
    )
    promotion.cars.add(car)
    return promotion


@pytest.fixture
def dealership_sale_history(
    dealership: Dealership, car: Car, user: User
) -> DealershipSaleHistory:
    return DealershipSaleHistory.objects.create(
        dealership=dealership, car=car, buyer=user, price=25000.00
    )


@pytest.mark.django_db
class TestDealershipSerializer:
    @pytest.fixture
    def valid_data(self) -> dict[str, Any]:
        return {
            "name": "New Dealership",
            "country": "DE",
            "city": "Berlin",
            "balance": 50000.00,
        }

    def test_valid_serializer_data(self, valid_data: dict[str, Any]) -> None:
        serializer = DealershipSerializer(data=valid_data)
        assert serializer.is_valid()

    def test_required_fields(self, valid_data: dict[str, Any]) -> None:
        required_fields = ["name", "country"]

        for field in required_fields:
            invalid_data = valid_data.copy()
            del invalid_data[field]

            serializer = DealershipSerializer(data=invalid_data)
            assert not serializer.is_valid()
            assert field in serializer.errors

    def test_unique_together_validation(
        self, valid_data: dict[str, Any], dealership: Dealership
    ) -> None:
        valid_data["name"] = dealership.name
        valid_data["country"] = dealership.country
        valid_data["city"] = dealership.city

        serializer = DealershipSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors

    def test_balance_validation(self, valid_data: dict[str, Any]) -> None:
        invalid_data = valid_data.copy()
        invalid_data["balance"] = -100.00

        serializer = DealershipSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert "balance" in serializer.errors

    def test_create_dealership(self, valid_data: dict[str, Any]) -> None:
        serializer = DealershipSerializer(data=valid_data)
        assert serializer.is_valid()

        dealership_obj = serializer.save()
        assert dealership_obj.name == "New Dealership"
        assert dealership_obj.country == "DE"
        assert dealership_obj.city == "Berlin"
        assert dealership_obj.balance == 50000.00
        assert dealership_obj.is_active is True

    def test_update_dealership(
        self, dealership: Dealership, valid_data: dict[str, Any]
    ) -> None:
        valid_data["name"] = "Updated Dealership"

        serializer = DealershipSerializer(
            instance=dealership, data=valid_data, partial=True
        )
        assert serializer.is_valid()

        updated_dealership = serializer.save()
        assert updated_dealership.name == "Updated Dealership"

    def test_serializer_fields(self, dealership: Dealership) -> None:
        serializer = DealershipSerializer(instance=dealership)

        expected_fields = {
            "id",
            "name",
            "country",
            "city",
            "balance",
            "created_at",
            "updated_at",
            "is_active",
        }

        assert serializer.data.keys() == expected_fields


@pytest.mark.django_db
class TestInventoryListSerializer:
    @pytest.fixture
    def valid_data(self, dealership: Dealership, car: Car) -> dict[str, Any]:
        return {
            "dealership": dealership.id,
            "car": car.id,
            "quantity": 10,
        }

    def test_valid_serializer_data(self, valid_data: dict[str, Any]) -> None:
        serializer = InventoryListSerializer(data=valid_data)
        assert serializer.is_valid()

    def test_required_fields(self, valid_data: dict[str, Any]) -> None:
        required_fields = ["dealership", "car"]

        for field in required_fields:
            invalid_data = valid_data.copy()
            del invalid_data[field]

            serializer = InventoryListSerializer(data=invalid_data)
            assert not serializer.is_valid()
            assert field in serializer.errors

    def test_quantity_validation(self, valid_data: dict[str, Any]) -> None:
        invalid_data = valid_data.copy()
        invalid_data["quantity"] = -5

        serializer = InventoryListSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert "quantity" in serializer.errors

    def test_unique_together_validation(
        self, valid_data: dict[str, Any], inventory: Inventory
    ) -> None:
        valid_data["dealership"] = inventory.dealership.id
        valid_data["car"] = inventory.car.id

        serializer = InventoryListSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors

    def test_create_inventory(
        self, valid_data: dict[str, Any], dealership: Dealership, car: Car
    ) -> None:
        valid_data["dealership"] = dealership.id
        valid_data["car"] = car.id

        serializer = InventoryListSerializer(data=valid_data)
        assert serializer.is_valid()

        inventory_obj = serializer.save()
        assert inventory_obj.dealership == dealership
        assert inventory_obj.car == car
        assert inventory_obj.quantity == 10
        assert inventory_obj.is_active is True


@pytest.mark.django_db
class TestInventoryDetailSerializer:
    def test_serializer_fields(self, inventory: Inventory) -> None:
        serializer = InventoryDetailSerializer(instance=inventory)

        expected_fields = {
            "id",
            "dealership",
            "car",
            "quantity",
            "created_at",
            "updated_at",
            "is_active",
        }

        assert serializer.data.keys() == expected_fields

    def test_nested_serializers(self, inventory: Inventory) -> None:
        serializer = InventoryDetailSerializer(instance=inventory)

        assert isinstance(serializer.data["dealership"], dict)
        assert isinstance(serializer.data["car"], dict)

        assert serializer.data["dealership"]["name"] == inventory.dealership.name
        assert "model_name" in serializer.data["car"]


@pytest.mark.django_db
class TestPreferredModelListSerializer:
    @pytest.fixture
    def valid_data(self, dealership: Dealership, car: Car) -> dict[str, Any]:
        return {
            "dealership": dealership.id,
            "car": car.id,
            "reason": "Popular model with high demand",
        }

    def test_valid_serializer_data(self, valid_data: dict[str, Any]) -> None:
        serializer = PreferredModelListSerializer(data=valid_data)
        assert serializer.is_valid()

    def test_required_fields(self, valid_data: dict[str, Any]) -> None:
        required_fields = ["dealership", "car"]

        for field in required_fields:
            invalid_data = valid_data.copy()
            del invalid_data[field]

            serializer = PreferredModelListSerializer(data=invalid_data)
            assert not serializer.is_valid()
            assert field in serializer.errors

    def test_unique_together_validation(
        self, valid_data: dict[str, Any], preferred_model: PreferredModel
    ) -> None:
        valid_data["dealership"] = preferred_model.dealership.id
        valid_data["car"] = preferred_model.car.id

        serializer = PreferredModelListSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors

    def test_create_preferred_model(
        self, valid_data: dict[str, Any], dealership: Dealership, car: Car
    ) -> None:
        serializer = PreferredModelListSerializer(data=valid_data)
        assert serializer.is_valid()

        preferred_model_obj = serializer.save()
        assert preferred_model_obj.dealership == dealership
        assert preferred_model_obj.car == car
        assert preferred_model_obj.reason == "Popular model with high demand"
        assert preferred_model_obj.is_active is True


@pytest.mark.django_db
class TestPreferredModelDetailSerializer:
    def test_serializer_fields(self, preferred_model: PreferredModel) -> None:
        serializer = PreferredModelDetailSerializer(instance=preferred_model)

        expected_fields = {
            "id",
            "dealership",
            "car",
            "reason",
            "created_at",
            "updated_at",
            "is_active",
        }

        assert set(serializer.data.keys()) == expected_fields

    def test_nested_serializers(self, preferred_model: PreferredModel) -> None:
        serializer = PreferredModelDetailSerializer(instance=preferred_model)

        assert isinstance(serializer.data["dealership"], dict)
        assert isinstance(serializer.data["car"], dict)

        assert serializer.data["dealership"]["name"] == preferred_model.dealership.name
        assert "model_name" in serializer.data["car"]


@pytest.mark.django_db
class TestDealershipPromotionListSerializer:
    @pytest.fixture
    def valid_data(self, dealership: Dealership, car: Car) -> dict[str, Any]:
        return {
            "dealership": dealership.id,
            "title": "Winter Sale",
            "discount_percent": 20.00,
            "start_date": "2024-12-01",
            "end_date": "2024-12-31",
            "cars": [car.id],
        }

    def test_valid_serializer_data(self, valid_data: dict[str, Any]) -> None:
        serializer = DealershipPromotionListSerializer(data=valid_data)
        assert serializer.is_valid()

    def test_required_fields(self, valid_data: dict[str, Any]) -> None:
        required_fields = ["dealership", "title", "start_date", "end_date"]

        for field in required_fields:
            invalid_data = valid_data.copy()
            del invalid_data[field]

            serializer = DealershipPromotionListSerializer(data=invalid_data)
            assert not serializer.is_valid()
            assert field in serializer.errors

    def test_discount_percent_validation(self, valid_data: dict[str, Any]) -> None:
        invalid_data = valid_data.copy()
        invalid_data["discount_percent"] = -10.00

        serializer = DealershipPromotionListSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert "discount_percent" in serializer.errors

        invalid_data["discount_percent"] = 150.00
        serializer = DealershipPromotionListSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert "discount_percent" in serializer.errors

        valid_data["discount_percent"] = 25.50
        serializer = DealershipPromotionListSerializer(data=valid_data)
        assert serializer.is_valid()

    def test_date_validation(self, valid_data: dict[str, Any]) -> None:
        invalid_data = valid_data.copy()
        invalid_data["start_date"] = "2024-12-31"
        invalid_data["end_date"] = "2024-12-01"

        serializer = DealershipPromotionListSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert "error" in serializer.errors

    def test_create_dealership_promotion(
        self, valid_data: dict[str, Any], dealership: Dealership, car: Car
    ) -> None:
        serializer = DealershipPromotionListSerializer(data=valid_data)
        assert serializer.is_valid()

        promotion = serializer.save()
        assert promotion.title == "Winter Sale"
        assert promotion.discount_percent == 20.00
        assert promotion.dealership == dealership
        assert car in promotion.cars.all()


@pytest.mark.django_db
class TestDealershipPromotionDetailSerializer:
    def test_serializer_fields(self, dealership_promotion: DealershipPromotion) -> None:
        serializer = DealershipPromotionDetailSerializer(instance=dealership_promotion)

        expected_fields = {
            "id",
            "dealership",
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

    def test_nested_serializers(
        self, dealership_promotion: DealershipPromotion
    ) -> None:
        serializer = DealershipPromotionDetailSerializer(instance=dealership_promotion)

        assert isinstance(serializer.data["dealership"], dict)
        assert isinstance(serializer.data["cars"], list)

        assert (
            serializer.data["dealership"]["name"]
            == dealership_promotion.dealership.name
        )
        assert len(serializer.data["cars"]) == 1
        assert "model_name" in serializer.data["cars"][0]


@pytest.mark.django_db
class TestDealershipSaleHistoryListSerializer:
    @pytest.fixture
    def valid_data(
        self, dealership: Dealership, car: Car, user: User
    ) -> dict[str, Any]:
        return {
            "dealership": dealership.id,
            "car": car.id,
            "buyer": user.id,
            "price": 27000.00,
        }

    def test_valid_serializer_data(self, valid_data: dict[str, Any]) -> None:
        serializer = DealershipSaleHistoryListSerializer(data=valid_data)
        assert serializer.is_valid()

    def test_required_fields(self, valid_data: dict[str, Any]) -> None:
        required_fields = ["dealership", "car", "buyer", "price"]

        for field in required_fields:
            invalid_data = valid_data.copy()
            del invalid_data[field]

            serializer = DealershipSaleHistoryListSerializer(data=invalid_data)
            assert not serializer.is_valid()
            assert field in serializer.errors

    def test_price_validation(self, valid_data: dict[str, Any]) -> None:
        invalid_data = valid_data.copy()
        invalid_data["price"] = -100.00

        serializer = DealershipSaleHistoryListSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert "price" in serializer.errors

    def test_create_dealership_sale_history(
        self, valid_data: dict[str, Any], dealership: Dealership, car: Car, user: User
    ) -> None:
        serializer = DealershipSaleHistoryListSerializer(data=valid_data)
        assert serializer.is_valid()

        sale_history = serializer.save()
        assert sale_history.dealership == dealership
        assert sale_history.car == car
        assert sale_history.buyer == user
        assert sale_history.price == 27000.00
        assert sale_history.is_active is True


@pytest.mark.django_db
class TestDealershipSaleHistoryDetailSerializer:
    def test_serializer_fields(
        self, dealership_sale_history: DealershipSaleHistory
    ) -> None:
        serializer = DealershipSaleHistoryDetailSerializer(
            instance=dealership_sale_history
        )

        expected_fields = {
            "id",
            "dealership",
            "car",
            "buyer",
            "price",
            "sale_date",
            "created_at",
            "updated_at",
            "is_active",
        }

        assert serializer.data.keys() == expected_fields

    def test_nested_serializers(
        self, dealership_sale_history: DealershipSaleHistory
    ) -> None:
        serializer = DealershipSaleHistoryDetailSerializer(
            instance=dealership_sale_history
        )

        assert isinstance(serializer.data["dealership"], dict)
        assert isinstance(serializer.data["car"], dict)
        assert isinstance(serializer.data["buyer"], dict)

        assert (
            serializer.data["dealership"]["name"]
            == dealership_sale_history.dealership.name
        )
        assert "model_name" in serializer.data["car"]
        assert "username" in serializer.data["buyer"]


@pytest.mark.django_db
class TestDealershipReportSerializer:
    def test_serializer_fields(self, dealership: Dealership) -> None:
        serializer = DealershipReportSerializer(instance=dealership)

        expected_fields = {
            "id",
            "name",
            "country",
            "city",
            "total_sales",
            "total_profit",
            "unique_buyers",
        }
        assert serializer.data.keys() == expected_fields

    def test_total_sales_calculation(
        self, dealership: Dealership, car: Car, user: User
    ) -> None:
        DealershipSaleHistory.objects.create(
            dealership=dealership, car=car, buyer=user, price=25000.00
        )
        DealershipSaleHistory.objects.create(
            dealership=dealership, car=car, buyer=user, price=30000.00
        )

        serializer = DealershipReportSerializer(instance=dealership)
        assert serializer.data["total_sales"] == 2

    def test_total_profit_calculation(
        self, dealership: Dealership, car: Car, user: User
    ) -> None:
        DealershipSaleHistory.objects.create(
            dealership=dealership, car=car, buyer=user, price=25000.00
        )
        DealershipSaleHistory.objects.create(
            dealership=dealership, car=car, buyer=user, price=30000.00
        )

        serializer = DealershipReportSerializer(instance=dealership)
        assert serializer.data["total_profit"] == 55000.0

    def test_unique_buyers_calculation(self, dealership: Dealership, car: Car) -> None:
        user1 = User.objects.create_user(
            username="buyer1", email="b1@example.com", password="pass"
        )
        user2 = User.objects.create_user(
            username="buyer2", email="b2@example.com", password="pass"
        )

        DealershipSaleHistory.objects.create(
            dealership=dealership, car=car, buyer=user1, price=25000.00
        )
        DealershipSaleHistory.objects.create(
            dealership=dealership, car=car, buyer=user2, price=30000.00
        )
        DealershipSaleHistory.objects.create(
            dealership=dealership, car=car, buyer=user1, price=27000.00
        )

        serializer = DealershipReportSerializer(instance=dealership)
        assert serializer.data["unique_buyers"] == 2
