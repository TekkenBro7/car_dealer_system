# pylint: disable=unused-argument
from datetime import date, timedelta

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from cars.models import BodyType, Car, CarBrand
from dealerships.models import Dealership
from suppliers.models import (
    Supplier,
    SupplierOffer,
    SupplierPromotion,
    SupplierSaleHistory,
)


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


# pylint: disable=too-many-locals
@pytest.fixture
def test_data() -> tuple[
    list[Supplier],
    list[Car],
    list[SupplierOffer],
    list[SupplierPromotion],
    list[SupplierSaleHistory],
]:
    supplier1 = Supplier.objects.create(
        name="Toyota Motors",
        country="JP",
        founded_year=1937,
        contact_email="contact@toyota.com",
        description="Japanese automaker",
    )
    supplier2 = Supplier.objects.create(
        name="BMW Group",
        country="DE",
        founded_year=1916,
        contact_email="info@bmw.com",
        description="German luxury vehicles",
    )
    supplier3 = Supplier.objects.create(
        name="Ford Motors",
        country="US",
        founded_year=1903,
        contact_email="support@ford.com",
        description="American automaker",
    )
    suppliers = [supplier1, supplier2, supplier3]

    brand1 = CarBrand.objects.create(name="Toyota", country="JP")
    brand2 = CarBrand.objects.create(name="BMW", country="DE")
    body_type1 = BodyType.objects.create(name="Sedan")
    body_type2 = BodyType.objects.create(name="SUV")

    car1 = Car.objects.create(brand=brand1, model_name="Camry", body_type=body_type1)
    car2 = Car.objects.create(brand=brand1, model_name="RAV4", body_type=body_type2)
    car3 = Car.objects.create(brand=brand2, model_name="3 Series", body_type=body_type1)
    car4 = Car.objects.create(brand=brand2, model_name="X5", body_type=body_type2)
    cars = [car1, car2, car3, car4]

    offers = [
        SupplierOffer.objects.create(supplier=supplier1, car=car1, price=25000.00),
        SupplierOffer.objects.create(supplier=supplier1, car=car2, price=28000.00),
        SupplierOffer.objects.create(supplier=supplier2, car=car3, price=35000.00),
        SupplierOffer.objects.create(supplier=supplier2, car=car4, price=55000.00),
        SupplierOffer.objects.create(supplier=supplier3, car=car1, price=24000.00),
    ]

    today = date.today()
    promotions = [
        SupplierPromotion.objects.create(
            supplier=supplier1,
            title="Summer Sale",
            description="Big discounts",
            discount_percent=15.00,
            start_date=today,
            end_date=today + timedelta(days=30),
        ),
        SupplierPromotion.objects.create(
            supplier=supplier2,
            title="Winter Special",
            description="Limited offer",
            discount_percent=20.00,
            start_date=today + timedelta(days=10),
            end_date=today + timedelta(days=40),
        ),
    ]
    promotions[0].cars.add(car1, car2)
    promotions[1].cars.add(car3, car4)

    dealership1 = Dealership.objects.create(
        name="NY Auto", country="US", city="New York", balance=100000
    )
    dealership2 = Dealership.objects.create(
        name="LA Cars", country="US", city="Los Angeles", balance=150000
    )

    sales = [
        SupplierSaleHistory.objects.create(
            supplier=supplier1, dealership=dealership1, car=car1, price=24500.00
        ),
        SupplierSaleHistory.objects.create(
            supplier=supplier1, dealership=dealership2, car=car2, price=27500.00
        ),
        SupplierSaleHistory.objects.create(
            supplier=supplier2, dealership=dealership1, car=car3, price=34500.00
        ),
    ]

    return suppliers, cars, offers, promotions, sales


@pytest.mark.django_db
class TestSupplierFiltering:
    def test_filter_suppliers_by_name(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/suppliers/", {"name": "Toyota"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert "Toyota" in response.data[0]["name"]

    def test_filter_suppliers_by_country(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/suppliers/", {"country": "DE"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["country"] == "DE"

    def test_search_suppliers_by_name(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/suppliers/", {"search": "Motors"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_search_suppliers_by_country(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/suppliers/", {"search": "US"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_order_suppliers_by_founded_year(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/suppliers/", {"ordering": "founded_year"})
        assert response.status_code == status.HTTP_200_OK
        years = [s["founded_year"] for s in response.data if s["founded_year"]]
        assert years == sorted(years)


@pytest.mark.django_db
class TestSupplierOfferFiltering:
    def test_filter_offers_by_supplier_name(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/supplier-offers/", {"supplier": "Toyota"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_filter_offers_by_car_model(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/supplier-offers/", {"car": "Camry"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_filter_offers_by_price_range(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get(
            "/api/supplier-offers/", {"price_min": 25000, "price_max": 40000}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_search_offers_by_supplier_name(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/supplier-offers/", {"search": "BMW"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_search_offers_by_car_model(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/supplier-offers/", {"search": "Series"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_order_offers_by_price(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/supplier-offers/", {"ordering": "price"})
        assert response.status_code == status.HTTP_200_OK
        prices = [float(o["price"]) for o in response.data]
        assert prices == sorted(prices)


@pytest.mark.django_db
class TestSupplierPromotionFiltering:
    def test_filter_promotions_by_supplier_name(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/supplier-promotions/", {"supplier": "Toyota"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert "Summer" in response.data[0]["title"]

    def test_filter_promotions_by_title(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/supplier-promotions/", {"title": "Winter"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_search_promotions_by_title(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/supplier-promotions/", {"search": "Sale"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_search_promotions_by_supplier(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/supplier-promotions/", {"search": "BMW"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_order_promotions_by_discount(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get(
            "/api/supplier-promotions/", {"ordering": "-discount_percent"}
        )
        assert response.status_code == status.HTTP_200_OK
        discounts = [float(p["discount_percent"]) for p in response.data]
        assert discounts == sorted(discounts, reverse=True)


@pytest.mark.django_db
class TestSupplierSaleHistoryFiltering:
    def test_filter_sales_by_supplier_name(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/supplier-sales/", {"supplier": "Toyota"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_filter_sales_by_dealership_name(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/supplier-sales/", {"dealership": "NY"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_filter_sales_by_car_model(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/supplier-sales/", {"car": "RAV4"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_filter_sales_by_price_range(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get(
            "/api/supplier-sales/", {"price_min": 27000, "price_max": 35000}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_search_sales_by_supplier(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/supplier-sales/", {"search": "BMW"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_search_sales_by_dealership(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/supplier-sales/", {"search": "LA"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_order_sales_by_price(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get("/api/supplier-sales/", {"ordering": "-price"})
        assert response.status_code == status.HTTP_200_OK
        prices = [float(s["price"]) for s in response.data]
        assert prices == sorted(prices, reverse=True)


@pytest.mark.django_db
class TestCombinedScenarios:
    def test_combined_filter_search_supplier_offers(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get(
            "/api/supplier-offers/",
            {
                "supplier": "Toyota",
                "price_min": 25000,
                "search": "Camry",
                "ordering": "-price",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_combined_filter_supplier_sales(
        self, api_client: APIClient, test_data: tuple
    ) -> None:
        response = api_client.get(
            "/api/supplier-sales/",
            {"supplier": "Toyota", "dealership": "NY", "ordering": "price"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
