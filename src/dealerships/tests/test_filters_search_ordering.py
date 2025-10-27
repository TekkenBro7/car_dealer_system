# pylint: disable=unused-argument
from datetime import date, timedelta

import pytest
from rest_framework import status
from rest_framework.test import APIClient

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
def api_client() -> APIClient:
    return APIClient()


# pylint: disable=too-many-locals
@pytest.fixture
def test_data() -> tuple[
    list[Dealership],
    list[Car],
    list[User],
    list[Inventory],
    list[PreferredModel],
    list[DealershipPromotion],
    list[DealershipSaleHistory],
]:
    dealership1 = Dealership.objects.create(
        name="NY Auto Center", country="US", city="New York", balance=200000.00
    )
    dealership2 = Dealership.objects.create(
        name="LA Motors", country="US", city="Los Angeles", balance=150000.00
    )
    dealership3 = Dealership.objects.create(
        name="Berlin Cars", country="DE", city="Berlin", balance=180000.00
    )
    dealerships = [dealership1, dealership2, dealership3]

    brand1 = CarBrand.objects.create(name="Toyota", country="JP")
    brand2 = CarBrand.objects.create(name="BMW", country="DE")
    body_type1 = BodyType.objects.create(name="Sedan")
    body_type2 = BodyType.objects.create(name="SUV")

    car1 = Car.objects.create(brand=brand1, model_name="Camry", body_type=body_type1)
    car2 = Car.objects.create(brand=brand1, model_name="RAV4", body_type=body_type2)
    car3 = Car.objects.create(brand=brand2, model_name="3 Series", body_type=body_type1)
    car4 = Car.objects.create(brand=brand2, model_name="X5", body_type=body_type2)
    cars = [car1, car2, car3, car4]

    user1 = User.objects.create_user(
        username="john_doe", email="john@test.com", password="pass123"
    )
    user2 = User.objects.create_user(
        username="jane_smith", email="jane@test.com", password="pass123"
    )
    users = [user1, user2]

    inventory = [
        Inventory.objects.create(dealership=dealership1, car=car1, quantity=10),
        Inventory.objects.create(dealership=dealership1, car=car2, quantity=5),
        Inventory.objects.create(dealership=dealership2, car=car3, quantity=8),
        Inventory.objects.create(dealership=dealership3, car=car4, quantity=3),
    ]

    preferred_models = [
        PreferredModel.objects.create(
            dealership=dealership1, car=car1, reason="Best seller"
        ),
        PreferredModel.objects.create(
            dealership=dealership1, car=car2, reason="High demand"
        ),
        PreferredModel.objects.create(
            dealership=dealership2, car=car3, reason="Luxury model"
        ),
    ]

    today = date.today()
    promotions = [
        DealershipPromotion.objects.create(
            dealership=dealership1,
            title="Summer Sale",
            description="Big discounts",
            discount_percent=15.00,
            start_date=today,
            end_date=today + timedelta(days=30),
        ),
        DealershipPromotion.objects.create(
            dealership=dealership2,
            title="Winter Special",
            description="Limited offer",
            discount_percent=20.00,
            start_date=today + timedelta(days=10),
            end_date=today + timedelta(days=40),
        ),
    ]
    promotions[0].cars.add(car1, car2)
    promotions[1].cars.add(car3)

    sales = [
        DealershipSaleHistory.objects.create(
            dealership=dealership1, car=car1, buyer=user1, price=25000.00
        ),
        DealershipSaleHistory.objects.create(
            dealership=dealership1, car=car2, buyer=user2, price=28000.00
        ),
        DealershipSaleHistory.objects.create(
            dealership=dealership2, car=car3, buyer=user1, price=35000.00
        ),
    ]

    return dealerships, cars, users, inventory, preferred_models, promotions, sales


@pytest.mark.django_db
class TestDealershipFiltering:
    def test_filter_dealerships_by_name(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/dealerships/", {"name": "NY"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert "NY" in response.data[0]["name"]

    def test_filter_dealerships_by_country(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/dealerships/", {"country": "US"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_filter_dealerships_by_city(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/dealerships/", {"city": "New York"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_filter_dealerships_by_balance_range(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get(
            "/api/dealerships/", {"balance_min": 160000, "balance_max": 190000}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_search_dealerships_by_name(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/dealerships/", {"search": "Auto"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_search_dealerships_by_city(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/dealerships/", {"search": "Los"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_order_dealerships_by_balance(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/dealerships/", {"ordering": "-balance"})
        assert response.status_code == status.HTTP_200_OK
        balances = [float(d["balance"]) for d in response.data]
        assert balances == sorted(balances, reverse=True)


@pytest.mark.django_db
class TestInventoryFiltering:
    def test_filter_inventory_by_dealership_name(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/dealership-inventories/", {"dealership": "NY"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_filter_inventory_by_car_model(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/dealership-inventories/", {"car": "Camry"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_filter_inventory_by_quantity_range(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get(
            "/api/dealership-inventories/", {"quantity_min": 5, "quantity_max": 8}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_search_inventory_by_dealership_name(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/dealership-inventories/", {"search": "LA"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_search_inventory_by_car_model(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/dealership-inventories/", {"search": "Series"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_order_inventory_by_quantity(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get(
            "/api/dealership-inventories/", {"ordering": "-quantity"}
        )
        assert response.status_code == status.HTTP_200_OK
        quantities = [i["quantity"] for i in response.data]
        assert quantities == sorted(quantities, reverse=True)


@pytest.mark.django_db
class TestPreferredModelFiltering:
    def test_filter_preferred_models_by_dealership_name(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/dealership-preffers/", {"dealership": "NY"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_filter_preferred_models_by_car_model(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/dealership-preffers/", {"car": "RAV4"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_search_preferred_models_by_dealership_name(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/dealership-preffers/", {"search": "LA"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_search_preferred_models_by_car_model(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/dealership-preffers/", {"search": "Series"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_search_preferred_models_by_reason(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/dealership-preffers/", {"search": "Best"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1


@pytest.mark.django_db
class TestDealershipPromotionFiltering:
    def test_filter_promotions_by_dealership_name(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/dealership-promotions/", {"dealership": "NY"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_filter_promotions_by_title(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/dealership-promotions/", {"title": "Summer"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_search_promotions_by_title(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/dealership-promotions/", {"search": "Special"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_search_promotions_by_dealership_name(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/dealership-promotions/", {"search": "LA"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_order_promotions_by_discount(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get(
            "/api/dealership-promotions/", {"ordering": "-discount_percent"}
        )
        assert response.status_code == status.HTTP_200_OK
        discounts = [float(p["discount_percent"]) for p in response.data]
        assert discounts == sorted(discounts, reverse=True)


@pytest.mark.django_db
class TestDealershipSaleHistoryFiltering:
    def test_filter_sales_by_dealership_name(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/dealership-sales/", {"dealership": "NY"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_filter_sales_by_buyer_username(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/dealership-sales/", {"buyer": "john"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_filter_sales_by_car_model(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/dealership-sales/", {"car": "Camry"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_filter_sales_by_price_range(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get(
            "/api/dealership-sales/", {"price_min": 26000, "price_max": 36000}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_search_sales_by_buyer_username(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/dealership-sales/", {"search": "jane"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_search_sales_by_car_model(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/dealership-sales/", {"search": "RAV4"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_order_sales_by_price(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/dealership-sales/", {"ordering": "-price"})
        assert response.status_code == status.HTTP_200_OK
        prices = [float(s["price"]) for s in response.data]
        assert prices == sorted(prices, reverse=True)


@pytest.mark.django_db
class TestCombinedScenarios:
    def test_combined_filter_search_inventory(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get(
            "/api/dealership-inventories/",
            {
                "dealership": "NY",
                "quantity_min": 5,
                "search": "Camry",
                "ordering": "-quantity",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_combined_filter_sales_history(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get(
            "/api/dealership-sales/",
            {"dealership": "NY", "buyer": "john", "ordering": "price"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
