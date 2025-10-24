# pylint: disable=unused-argument
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from cars.models import BodyType, Car, CarBrand


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def test_data() -> tuple[CarBrand, BodyType, list[Car]]:
    brand1 = CarBrand.objects.create(name="Toyota", country="JP")
    brand2 = CarBrand.objects.create(name="BMW", country="DE")

    body_type1 = BodyType.objects.create(name="Sedan")
    body_type2 = BodyType.objects.create(name="SUV")

    cars = [
        Car.objects.create(brand=brand1, model_name="Camry", body_type=body_type1),
        Car.objects.create(brand=brand1, model_name="RAV4", body_type=body_type2),
        Car.objects.create(brand=brand2, model_name="X5", body_type=body_type2),
        Car.objects.create(brand=brand2, model_name="3 Series", body_type=body_type1),
    ]
    return brand1, body_type1, cars


@pytest.mark.django_db
class TestCarFiltering:
    def test_filter_cars_by_brand(
        self, api_client: APIClient, test_data: tuple[CarBrand, BodyType, list[Car]]
    ) -> None:
        response = api_client.get("/api/cars/", {"brand": "Toyota"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_filter_cars_by_body_type(
        self, api_client: APIClient, test_data: tuple[CarBrand, BodyType, list[Car]]
    ) -> None:
        response = api_client.get("/api/cars/", {"body_type": "Sedan"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_filter_cars_by_model_name(
        self, api_client: APIClient, test_data: tuple[CarBrand, BodyType, list[Car]]
    ) -> None:
        response = api_client.get("/api/cars/", {"model_name": "Camry"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["model_name"] == "Camry"

    def test_filter_cars_by_partial_model_name(
        self, api_client: APIClient, test_data: tuple[CarBrand, BodyType, list[Car]]
    ) -> None:
        response = api_client.get("/api/cars/", {"model_name": "Series"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert "Series" in response.data[0]["model_name"]


@pytest.mark.django_db
class TestCarSearch:
    def test_search_cars_by_model_name(
        self, api_client: APIClient, test_data: tuple[CarBrand, BodyType, list[Car]]
    ) -> None:
        response = api_client.get("/api/cars/", {"search": "Camry"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["model_name"] == "Camry"

    def test_search_cars_by_brand_name(
        self, api_client: APIClient, test_data: tuple[CarBrand, BodyType, list[Car]]
    ) -> None:
        response = api_client.get("/api/cars/", {"search": "BMW"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_search_cars_by_body_type(
        self, api_client: APIClient, test_data: tuple[CarBrand, BodyType, list[Car]]
    ) -> None:
        response = api_client.get("/api/cars/", {"search": "SUV"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2


@pytest.mark.django_db
class TestCarOrdering:
    def test_order_cars_by_model_name_asc(
        self, api_client: APIClient, test_data: tuple[CarBrand, BodyType, list[Car]]
    ) -> None:
        response = api_client.get("/api/cars/", {"ordering": "model_name"})
        assert response.status_code == status.HTTP_200_OK
        model_names = [car["model_name"] for car in response.data]
        assert model_names == sorted(model_names)

    def test_order_cars_by_model_name_desc(
        self, api_client: APIClient, test_data: tuple[CarBrand, BodyType, list[Car]]
    ) -> None:
        response = api_client.get("/api/cars/", {"ordering": "-model_name"})
        assert response.status_code == status.HTTP_200_OK
        model_names = [car["model_name"] for car in response.data]
        assert model_names == sorted(model_names, reverse=True)

    def test_default_ordering(
        self, api_client: APIClient, test_data: tuple[CarBrand, BodyType, list[Car]]
    ) -> None:
        response = api_client.get("/api/cars/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 4


@pytest.mark.django_db
class TestCombinedFilterSearchOrder:
    def test_combined_filter_search_cars(
        self, api_client: APIClient, test_data: tuple[CarBrand, BodyType, list[Car]]
    ) -> None:
        response = api_client.get(
            "/api/cars/", {"brand": "Toyota", "search": "RAV", "ordering": "model_name"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["model_name"] == "RAV4"

    def test_combined_search_multiple_conditions(
        self, api_client: APIClient, test_data: tuple[CarBrand, BodyType, list[Car]]
    ) -> None:
        response = api_client.get(
            "/api/cars/", {"body_type": "Sedan", "ordering": "-model_name"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        model_names = [car["model_name"] for car in response.data]
        assert model_names == sorted(model_names, reverse=True)
