import pytest
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from cars.models import BodyType, Car, CarBrand
from offers.models import Offer, OfferStatus
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
def offer(user: User, car: Car) -> Offer:
    return Offer.objects.create(
        buyer=user, car=car, max_price=25000.00, status=OfferStatus.PENDING
    )


@pytest.mark.django_db
class TestOfferViewSet:
    # pylint: disable=unused-argument
    def test_list_offers(self, api_client: APIClient, offer: Offer) -> None:
        response = api_client.get("/api/offers/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["max_price"] == "25000.00"

    def test_retrieve_offer_with_detail_serializer(
        self, api_client: APIClient, offer: Offer
    ) -> None:
        response = api_client.get(f"/api/offers/{offer.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["max_price"] == "25000.00"
        assert response.data["status"] == "pending"
        assert isinstance(response.data["buyer"], dict)
        assert isinstance(response.data["car"], dict)
        assert response.data["buyer"]["username"] == "testuser"

    def test_create_offer(self, api_client: APIClient, user: User, car: Car) -> None:
        offer_data = {
            "buyer": user.id,
            "car": car.id,
            "max_price": 30000.00,
        }
        response = api_client.post("/api/offers/", offer_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["max_price"] == "30000.00"
        assert response.data["status"] == "pending"
        assert Offer.objects.filter(max_price=30000.00).exists()

    def test_create_offer_with_default_status(
        self, api_client: APIClient, user: User, car: Car
    ) -> None:
        offer_data = {"buyer": user.id, "car": car.id, "max_price": 28000.00}
        response = api_client.post("/api/offers/", offer_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == "pending"

    def test_update_offer(self, api_client: APIClient, offer: Offer) -> None:
        update_data = {"max_price": 27000.00, "status": OfferStatus.ACCEPTED}
        response = api_client.patch(f"/api/offers/{offer.id}/", update_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["max_price"] == "27000.00"
        assert response.data["status"] == "accepted"

        offer.refresh_from_db()
        assert offer.max_price == 27000.00
        assert offer.status == OfferStatus.ACCEPTED

    def test_delete_offer(self, api_client: APIClient, offer: Offer) -> None:
        response = api_client.delete(f"/api/offers/{offer.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_update_offer_max_price_only(
        self, api_client: APIClient, offer: Offer
    ) -> None:
        update_data = {"max_price": 26000.00}
        response = api_client.patch(f"/api/offers/{offer.id}/", update_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["max_price"] == "26000.00"

        offer.refresh_from_db()
        assert offer.max_price == 26000.00
        assert offer.status == OfferStatus.PENDING
