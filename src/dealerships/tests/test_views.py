from datetime import date

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from cars.models import BodyType, Car, CarBrand
from dealerships.models import (
    Dealership,
    DealershipPromotion,
    DealershipSaleHistory,
    Inventory,
    PreferredModel,
)
from users.models import User


@pytest.fixture
def user() -> User:
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        role="admin",
    )


@pytest.fixture
def api_client(user: User) -> APIClient:
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


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
class TestDealershipViewSet:
    # pylint: disable=unused-argument
    def test_list_dealerships(
        self, api_client: APIClient, dealership: Dealership
    ) -> None:
        response = api_client.get("/api/dealerships/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Test Dealership"

    def test_retrieve_dealership(
        self, api_client: APIClient, dealership: Dealership
    ) -> None:
        response = api_client.get(f"/api/dealerships/{dealership.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Test Dealership"
        assert response.data["country"] == "US"
        assert response.data["city"] == "New York"

    def test_create_dealership(self, api_client: APIClient) -> None:
        dealership_data = {
            "name": "New Dealership",
            "country": "DE",
            "city": "Berlin",
            "balance": 50000.00,
        }
        response = api_client.post("/api/dealerships/", dealership_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "New Dealership"
        assert Dealership.objects.filter(name="New Dealership").exists()

    def test_update_dealership(
        self, api_client: APIClient, dealership: Dealership
    ) -> None:
        update_data = {"name": "Updated Dealership"}
        response = api_client.patch(f"/api/dealerships/{dealership.id}/", update_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Dealership"

        dealership.refresh_from_db()
        assert dealership.name == "Updated Dealership"

    def test_delete_dealership(
        self, api_client: APIClient, dealership: Dealership
    ) -> None:
        response = api_client.delete(f"/api/dealerships/{dealership.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestInventoryViewSet:
    # pylint: disable=unused-argument
    def test_list_inventories(
        self, api_client: APIClient, inventory: Inventory
    ) -> None:
        response = api_client.get("/api/dealership-inventories/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["quantity"] == 5

    def test_retrieve_inventory_with_detail_serializer(
        self, api_client: APIClient, inventory: Inventory
    ) -> None:
        response = api_client.get(f"/api/dealership-inventories/{inventory.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["quantity"] == 5
        assert isinstance(response.data["dealership"], dict)
        assert isinstance(response.data["car"], dict)
        assert response.data["dealership"]["name"] == "Test Dealership"

    def test_create_inventory(
        self, api_client: APIClient, dealership: Dealership, car: Car
    ) -> None:
        inventory_data = {"dealership": dealership.id, "car": car.id, "quantity": 10}
        response = api_client.post("/api/dealership-inventories/", inventory_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["quantity"] == 10
        assert Inventory.objects.filter(quantity=10).exists()

    def test_update_inventory(
        self, api_client: APIClient, inventory: Inventory
    ) -> None:
        update_data = {"quantity": 8}
        response = api_client.patch(
            f"/api/dealership-inventories/{inventory.id}/", update_data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["quantity"] == 8

        inventory.refresh_from_db()
        assert inventory.quantity == 8

    def test_delete_inventory(
        self, api_client: APIClient, inventory: Inventory
    ) -> None:
        response = api_client.delete(f"/api/dealership-inventories/{inventory.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_create_inventory_duplicate(
        self, api_client: APIClient, inventory: Inventory
    ) -> None:
        duplicate_data = {
            "dealership": inventory.dealership.id,
            "car": inventory.car.id,
            "quantity": 15,
        }
        response = api_client.post("/api/dealership-inventories/", duplicate_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data

    def test_create_inventory_negative_quantity(
        self, api_client: APIClient, dealership: Dealership, car: Car
    ) -> None:
        invalid_data = {"dealership": dealership.id, "car": car.id, "quantity": -5}
        response = api_client.post("/api/dealership-inventories/", invalid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "quantity" in response.data


@pytest.mark.django_db
class TestPreferredModelViewSet:
    # pylint: disable=unused-argument
    def test_list_preferred_models(
        self, api_client: APIClient, preferred_model: PreferredModel
    ) -> None:
        response = api_client.get("/api/dealership-preffers/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["reason"] == "High demand model"

    def test_retrieve_preferred_model_with_detail_serializer(
        self, api_client: APIClient, preferred_model: PreferredModel
    ) -> None:
        response = api_client.get(f"/api/dealership-preffers/{preferred_model.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["reason"] == "High demand model"
        assert isinstance(response.data["dealership"], dict)
        assert isinstance(response.data["car"], dict)
        assert response.data["dealership"]["name"] == "Test Dealership"

    def test_create_preferred_model(
        self, api_client: APIClient, dealership: Dealership, car: Car
    ) -> None:
        preferred_data = {
            "dealership": dealership.id,
            "car": car.id,
            "reason": "Popular model",
        }
        response = api_client.post("/api/dealership-preffers/", preferred_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["reason"] == "Popular model"
        assert PreferredModel.objects.filter(reason="Popular model").exists()

    def test_update_preferred_model(
        self, api_client: APIClient, preferred_model: PreferredModel
    ) -> None:
        update_data = {"reason": "Updated reason"}
        response = api_client.patch(
            f"/api/dealership-preffers/{preferred_model.id}/", update_data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["reason"] == "Updated reason"

        preferred_model.refresh_from_db()
        assert preferred_model.reason == "Updated reason"

    def test_delete_preferred_model(
        self, api_client: APIClient, preferred_model: PreferredModel
    ) -> None:
        response = api_client.delete(f"/api/dealership-preffers/{preferred_model.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestDealershipPromotionViewSet:
    # pylint: disable=unused-argument
    def test_list_dealership_promotions(
        self, api_client: APIClient, dealership_promotion: DealershipPromotion
    ) -> None:
        response = api_client.get("/api/dealership-promotions/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["title"] == "Summer Sale"

    def test_retrieve_dealership_promotion_with_detail_serializer(
        self, api_client: APIClient, dealership_promotion: DealershipPromotion
    ) -> None:
        response = api_client.get(
            f"/api/dealership-promotions/{dealership_promotion.id}/"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Summer Sale"
        assert isinstance(response.data["dealership"], dict)
        assert isinstance(response.data["cars"], list)
        assert response.data["dealership"]["name"] == "Test Dealership"
        assert len(response.data["cars"]) == 1

    def test_create_dealership_promotion(
        self, api_client: APIClient, dealership: Dealership, car: Car
    ) -> None:
        promotion_data = {
            "dealership": dealership.id,
            "title": "Winter Sale",
            "discount_percent": 20.00,
            "start_date": "2024-12-01",
            "end_date": "2024-12-31",
            "cars": [car.id],
        }
        response = api_client.post("/api/dealership-promotions/", promotion_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "Winter Sale"
        assert response.data["discount_percent"] == "20.00"
        assert DealershipPromotion.objects.filter(title="Winter Sale").exists()

    def test_update_dealership_promotion(
        self, api_client: APIClient, dealership_promotion: DealershipPromotion
    ) -> None:
        update_data = {"title": "Updated Sale"}
        response = api_client.patch(
            f"/api/dealership-promotions/{dealership_promotion.id}/", update_data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Updated Sale"

        dealership_promotion.refresh_from_db()
        assert dealership_promotion.title == "Updated Sale"

    def test_delete_dealership_promotion(
        self, api_client: APIClient, dealership_promotion: DealershipPromotion
    ) -> None:
        response = api_client.delete(
            f"/api/dealership-promotions/{dealership_promotion.id}/"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_create_dealership_promotion_invalid_dates(
        self, api_client: APIClient, dealership: Dealership, car: Car
    ) -> None:
        invalid_data = {
            "dealership": dealership.id,
            "title": "Invalid Sale",
            "discount_percent": 10.00,
            "start_date": "2024-12-31",
            "end_date": "2024-12-01",
            "cars": [car.id],
        }
        response = api_client.post("/api/dealership-promotions/", invalid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    def test_create_dealership_promotion_invalid_discount(
        self, api_client: APIClient, dealership: Dealership, car: Car
    ) -> None:
        invalid_data = {
            "dealership": dealership.id,
            "title": "Invalid Discount",
            "discount_percent": 150.00,
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "cars": [car.id],
        }
        response = api_client.post("/api/dealership-promotions/", invalid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "discount_percent" in response.data


@pytest.mark.django_db
class TestDealershipSaleHistoryViewSet:
    # pylint: disable=unused-argument
    def test_list_dealership_sales(
        self, api_client: APIClient, dealership_sale_history: DealershipSaleHistory
    ) -> None:
        response = api_client.get("/api/dealership-sales/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["price"] == "25000.00"

    def test_retrieve_dealership_sale_with_detail_serializer(
        self, api_client: APIClient, dealership_sale_history: DealershipSaleHistory
    ) -> None:
        response = api_client.get(
            f"/api/dealership-sales/{dealership_sale_history.id}/"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["price"] == "25000.00"
        assert isinstance(response.data["dealership"], dict)
        assert isinstance(response.data["car"], dict)
        assert isinstance(response.data["buyer"], dict)
        assert response.data["dealership"]["name"] == "Test Dealership"
        assert response.data["buyer"]["username"] == "testuser"

    def test_create_dealership_sale_history(
        self, api_client: APIClient, dealership: Dealership, car: Car, user: User
    ) -> None:
        sale_data = {
            "dealership": dealership.id,
            "car": car.id,
            "buyer": user.id,
            "price": 27000.00,
        }
        response = api_client.post("/api/dealership-sales/", sale_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["price"] == "27000.00"
        assert DealershipSaleHistory.objects.filter(price=27000.00).exists()

    def test_update_dealership_sale_history(
        self, api_client: APIClient, dealership_sale_history: DealershipSaleHistory
    ) -> None:
        update_data = {"price": 26000.00}
        response = api_client.patch(
            f"/api/dealership-sales/{dealership_sale_history.id}/", update_data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["price"] == "26000.00"

        dealership_sale_history.refresh_from_db()
        assert dealership_sale_history.price == 26000.00

    def test_delete_dealership_sale_history(
        self, api_client: APIClient, dealership_sale_history: DealershipSaleHistory
    ) -> None:
        response = api_client.delete(
            f"/api/dealership-sales/{dealership_sale_history.id}/"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
