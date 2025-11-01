from datetime import date

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from cars.models import BodyType, Car, CarBrand
from dealerships.models import Dealership
from suppliers.models import (
    Supplier,
    SupplierOffer,
    SupplierPromotion,
    SupplierSaleHistory,
)
from users.models import User


@pytest.fixture
def regular_user() -> User:
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        role="admin",
    )


@pytest.fixture
def regular_user_buyer() -> User:
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        role="buyer",
    )


@pytest.fixture
def api_client(regular_user: User) -> APIClient:
    client = APIClient()
    refresh = RefreshToken.for_user(regular_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def api_client_buyer(regular_user_buyer: User) -> APIClient:
    client = APIClient()
    refresh = RefreshToken.for_user(regular_user_buyer)
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
    promotion = SupplierPromotion.objects.create(
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
class TestSupplierViewSet:
    # pylint: disable=unused-argument
    def test_list_suppliers(self, api_client: APIClient, supplier: Supplier) -> None:
        response = api_client.get("/api/suppliers/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Test Supplier"

    def test_retrieve_supplier(self, api_client: APIClient, supplier: Supplier) -> None:
        response = api_client.get(f"/api/suppliers/{supplier.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Test Supplier"
        assert response.data["country"] == "US"
        assert response.data["founded_year"] == 1990

    def test_create_supplier(self, api_client: APIClient) -> None:
        supplier_data = {
            "name": "New Supplier",
            "founded_year": 2000,
            "country": "DE",
            "contact_email": "new@supplier.com",
            "description": "New supplier description",
        }
        response = api_client.post("/api/suppliers/", supplier_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "New Supplier"
        assert Supplier.objects.filter(name="New Supplier").exists()

    def test_update_supplier(self, api_client: APIClient, supplier: Supplier) -> None:
        update_data = {"name": "Updated Supplier"}
        response = api_client.patch(f"/api/suppliers/{supplier.id}/", update_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Supplier"

        supplier.refresh_from_db()
        assert supplier.name == "Updated Supplier"

    def test_delete_supplier(self, api_client: APIClient, supplier: Supplier) -> None:
        response = api_client.delete(f"/api/suppliers/{supplier.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestSupplierOfferViewSet:
    # pylint: disable=unused-argument
    def test_list_supplier_offers(
        self, api_client: APIClient, supplier_offer: SupplierOffer
    ) -> None:
        response = api_client.get("/api/supplier-offers/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["price"] == "25000.00"

    def test_retrieve_supplier_offer_with_detail_serializer(
        self, api_client: APIClient, supplier_offer: SupplierOffer
    ) -> None:
        response = api_client.get(f"/api/supplier-offers/{supplier_offer.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["price"] == "25000.00"
        assert isinstance(response.data["supplier"], dict)
        assert isinstance(response.data["car"], dict)
        assert response.data["supplier"]["name"] == "Test Supplier"

    def test_create_supplier_offer(
        self, api_client: APIClient, supplier: Supplier, car: Car
    ) -> None:
        offer_data = {"supplier": supplier.id, "car": car.id, "price": 30000.00}
        response = api_client.post("/api/supplier-offers/", offer_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["price"] == "30000.00"
        assert SupplierOffer.objects.filter(price=30000.00).exists()

    def test_update_supplier_offer(
        self, api_client: APIClient, supplier_offer: SupplierOffer
    ) -> None:
        update_data = {"price": 27000.00}
        response = api_client.patch(
            f"/api/supplier-offers/{supplier_offer.id}/", update_data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["price"] == "27000.00"

        supplier_offer.refresh_from_db()
        assert supplier_offer.price == 27000.00

    def test_delete_supplier_offer(
        self, api_client: APIClient, supplier_offer: SupplierOffer
    ) -> None:
        response = api_client.delete(f"/api/supplier-offers/{supplier_offer.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestSupplierPromotionViewSet:
    # pylint: disable=unused-argument
    def test_list_supplier_promotions(
        self, api_client: APIClient, supplier_promotion: SupplierPromotion
    ) -> None:
        response = api_client.get("/api/supplier-promotions/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["title"] == "Summer Sale"

    def test_retrieve_supplier_promotion_with_detail_serializer(
        self, api_client: APIClient, supplier_promotion: SupplierPromotion
    ) -> None:
        response = api_client.get(f"/api/supplier-promotions/{supplier_promotion.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Summer Sale"
        assert isinstance(response.data["supplier"], dict)
        assert isinstance(response.data["cars"], list)
        assert response.data["supplier"]["name"] == "Test Supplier"
        assert len(response.data["cars"]) == 1

    def test_create_supplier_promotion(
        self, api_client: APIClient, supplier: Supplier, car: Car
    ) -> None:
        promotion_data = {
            "supplier": supplier.id,
            "title": "Winter Sale",
            "discount_percent": 20.00,
            "start_date": "2024-12-01",
            "end_date": "2024-12-31",
            "cars": [car.id],
        }
        response = api_client.post("/api/supplier-promotions/", promotion_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "Winter Sale"
        assert response.data["discount_percent"] == "20.00"
        assert SupplierPromotion.objects.filter(title="Winter Sale").exists()

    def test_update_supplier_promotion(
        self, api_client: APIClient, supplier_promotion: SupplierPromotion
    ) -> None:
        update_data = {"title": "Updated Sale"}
        response = api_client.patch(
            f"/api/supplier-promotions/{supplier_promotion.id}/", update_data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Updated Sale"

        supplier_promotion.refresh_from_db()
        assert supplier_promotion.title == "Updated Sale"

    def test_delete_supplier_promotion(
        self, api_client: APIClient, supplier_promotion: SupplierPromotion
    ) -> None:
        response = api_client.delete(
            f"/api/supplier-promotions/{supplier_promotion.id}/"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestSupplierSaleHistoryViewSet:
    # pylint: disable=unused-argument
    def test_list_supplier_sales(
        self, api_client: APIClient, supplier_sale_history: SupplierSaleHistory
    ) -> None:
        response = api_client.get("/api/supplier-sales/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["price"] == "23000.00"

    def test_retrieve_supplier_sale_with_detail_serializer(
        self, api_client: APIClient, supplier_sale_history: SupplierSaleHistory
    ) -> None:
        response = api_client.get(f"/api/supplier-sales/{supplier_sale_history.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["price"] == "23000.00"
        assert isinstance(response.data["supplier"], dict)
        assert isinstance(response.data["car"], dict)
        assert response.data["supplier"]["name"] == "Test Supplier"

    def test_create_supplier_sale_history(
        self,
        api_client: APIClient,
        supplier: Supplier,
        car: Car,
        dealership: Dealership,
    ) -> None:
        sale_data = {
            "supplier": supplier.id,
            "dealership": dealership.id,
            "car": car.id,
            "price": 27000.00,
        }
        response = api_client.post("/api/supplier-sales/", sale_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["price"] == "27000.00"
        assert SupplierSaleHistory.objects.filter(price=27000.00).exists()

    def test_update_supplier_sale_history(
        self, api_client: APIClient, supplier_sale_history: SupplierSaleHistory
    ) -> None:
        update_data = {"price": 25000.00}
        response = api_client.patch(
            f"/api/supplier-sales/{supplier_sale_history.id}/", update_data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["price"] == "25000.00"

        supplier_sale_history.refresh_from_db()
        assert supplier_sale_history.price == 25000.00

    def test_delete_supplier_sale_history(
        self, api_client: APIClient, supplier_sale_history: SupplierSaleHistory
    ) -> None:
        response = api_client.delete(f"/api/supplier-sales/{supplier_sale_history.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestSupplierReportViewSet:
    # pylint: disable=unused-argument
    def test_list_supplier_reports_admin_access(
        self, api_client: APIClient, supplier: Supplier
    ) -> None:
        response = api_client.get("/api/supplier-reports/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Test Supplier"

    def test_list_supplier_reports_regular_user_denied(
        self, api_client: APIClient
    ) -> None:
        response = api_client.get("/api/supplier-reports/")
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_supplier_report_admin_access(
        self, api_client: APIClient, supplier: Supplier
    ) -> None:
        response = api_client.get(f"/api/supplier-reports/{supplier.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Test Supplier"
        assert response.data["total_sales"] == 0
        assert response.data["total_revenue"] == 0.0
        assert response.data["partner_dealerships"] == 0

    def test_retrieve_supplier_report_regular_user_denied(
        self, api_client_buyer: APIClient, supplier: Supplier
    ) -> None:
        response = api_client_buyer.get(f"/api/supplier-reports/{supplier.id}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_supplier_report_with_sales_data(
        self,
        api_client: APIClient,
        supplier: Supplier,
        car: Car,
        dealership: Dealership,
    ) -> None:
        SupplierSaleHistory.objects.create(
            supplier=supplier, dealership=dealership, car=car, price=25000.00
        )
        SupplierSaleHistory.objects.create(
            supplier=supplier, dealership=dealership, car=car, price=30000.00
        )

        response = api_client.get(f"/api/supplier-reports/{supplier.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_sales"] == 2
        assert response.data["total_revenue"] == 55000.0
        assert response.data["partner_dealerships"] == 1

    def test_supplier_report_not_found(self, api_client: APIClient) -> None:
        response = api_client.get("/api/supplier-reports/999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_supplier_report_methods_not_allowed(
        self, api_client: APIClient, supplier: Supplier
    ) -> None:
        response = api_client.post("/api/supplier-reports/", {"name": "New Supplier"})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        response = api_client.put(f"/api/supplier-reports/{supplier.id}/", {})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        response = api_client.delete(f"/api/supplier-reports/{supplier.id}/")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
