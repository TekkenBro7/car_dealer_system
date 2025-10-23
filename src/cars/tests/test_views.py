import pytest
from rest_framework import status
from rest_framework.test import APIClient

from cars.models import BodyType, Car, CarBrand


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def car_brand() -> CarBrand:
    return CarBrand.objects.create(name="Toyota", country="JP")


@pytest.fixture
def body_type() -> BodyType:
    return BodyType.objects.create(name="Sedan")


@pytest.fixture
def car(car_brand: CarBrand, body_type: BodyType) -> Car:
    return Car.objects.create(brand=car_brand, model_name="Camry", body_type=body_type)


@pytest.mark.django_db
class TestCarBrandViewSet:
    # pylint: disable=unused-argument
    def test_list_brands(self, api_client: APIClient, car_brand: CarBrand) -> None:
        response = api_client.get("/api/brands/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Toyota"

    def test_retrieve_brand(self, api_client: APIClient, car_brand: CarBrand) -> None:
        response = api_client.get(f"/api/brands/{car_brand.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Toyota"
        assert response.data["country"] == "JP"

    def test_create_brand(self, api_client: APIClient) -> None:
        brand_data = {"name": "Honda", "country": "JP"}
        response = api_client.post("/api/brands/", brand_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Honda"
        assert CarBrand.objects.filter(name="Honda").exists()

    def test_update_brand(self, api_client: APIClient, car_brand: CarBrand) -> None:
        update_data = {"name": "Toyota Motors"}
        response = api_client.patch(f"/api/brands/{car_brand.id}/", update_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Toyota Motors"

        car_brand.refresh_from_db()
        assert car_brand.name == "Toyota Motors"

    def test_delete_brand(self, api_client: APIClient, car_brand: CarBrand) -> None:
        response = api_client.delete(f"/api/brands/{car_brand.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestBodyTypeViewSet:
    # pylint: disable=unused-argument
    def test_list_body_types(self, api_client: APIClient, body_type: BodyType) -> None:
        response = api_client.get("/api/body-types/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Sedan"

    def test_retrieve_body_type(
        self, api_client: APIClient, body_type: BodyType
    ) -> None:
        response = api_client.get(f"/api/body-types/{body_type.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Sedan"

    def test_create_body_type(self, api_client: APIClient) -> None:
        body_type_data = {"name": "SUV"}
        response = api_client.post("/api/body-types/", body_type_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "SUV"
        assert BodyType.objects.filter(name="SUV").exists()

    def test_update_body_type(self, api_client: APIClient, body_type: BodyType) -> None:
        update_data = {"name": "Sedan Premium"}
        response = api_client.patch(f"/api/body-types/{body_type.id}/", update_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Sedan Premium"

        body_type.refresh_from_db()
        assert body_type.name == "Sedan Premium"

    def test_delete_body_type(self, api_client: APIClient, body_type: BodyType) -> None:
        response = api_client.delete(f"/api/body-types/{body_type.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestCarViewSet:
    # pylint: disable=unused-argument
    def test_list_cars(self, api_client: APIClient, car: Car) -> None:
        response = api_client.get("/api/cars/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["model_name"] == "Camry"

    def test_retrieve_car_with_detail_serializer(
        self, api_client: APIClient, car: Car
    ) -> None:
        response = api_client.get(f"/api/cars/{car.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["model_name"] == "Camry"
        assert isinstance(response.data["brand"], dict)
        assert isinstance(response.data["body_type"], dict)
        assert response.data["brand"]["name"] == "Toyota"
        assert response.data["body_type"]["name"] == "Sedan"

    def test_create_car(
        self, api_client: APIClient, car_brand: CarBrand, body_type: BodyType
    ) -> None:
        car_data = {
            "model_name": "Corolla",
            "brand": car_brand.id,
            "body_type": body_type.id,
        }
        response = api_client.post("/api/cars/", car_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["model_name"] == "Corolla"
        assert Car.objects.filter(model_name="Corolla").exists()

    def test_create_car_without_body_type(
        self, api_client: APIClient, car_brand: CarBrand
    ) -> None:
        car_data = {"model_name": "Corolla", "brand": car_brand.id}
        response = api_client.post("/api/cars/", car_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["model_name"] == "Corolla"

    def test_update_car(self, api_client: APIClient, car: Car) -> None:
        update_data = {"model_name": "Camry Hybrid"}
        response = api_client.patch(f"/api/cars/{car.id}/", update_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["model_name"] == "Camry Hybrid"

        car.refresh_from_db()
        assert car.model_name == "Camry Hybrid"

    def test_delete_car(self, api_client: APIClient, car: Car) -> None:
        response = api_client.delete(f"/api/cars/{car.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
