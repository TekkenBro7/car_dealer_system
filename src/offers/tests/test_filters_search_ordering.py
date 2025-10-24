# pylint: disable=unused-argument
from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from cars.models import BodyType, Car, CarBrand
from offers.models import Offer, OfferStatus
from users.models import User


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def test_data() -> tuple[list[User], list[Car], list[Offer]]:
    user1 = User.objects.create_user(
        username="john_doe", email="john@test.com", password="pass123"
    )
    user2 = User.objects.create_user(
        username="jane_smith", email="jane@test.com", password="pass123"
    )
    user3 = User.objects.create_user(
        username="bob_wilson", email="bob@test.com", password="pass123"
    )
    users = [user1, user2, user3]

    brand1 = CarBrand.objects.create(name="Toyota", country="JP")
    brand2 = CarBrand.objects.create(name="BMW", country="DE")
    body_type = BodyType.objects.create(name="Sedan")

    car1 = Car.objects.create(brand=brand1, model_name="Camry", body_type=body_type)
    car2 = Car.objects.create(brand=brand1, model_name="Corolla", body_type=body_type)
    car3 = Car.objects.create(brand=brand2, model_name="3 Series", body_type=body_type)
    cars = [car1, car2, car3]

    offers = [
        Offer.objects.create(
            buyer=user1,
            car=car1,
            max_price=Decimal("25000.00"),
            status=OfferStatus.PENDING,
        ),
        Offer.objects.create(
            buyer=user2,
            car=car2,
            max_price=Decimal("20000.00"),
            status=OfferStatus.ACCEPTED,
        ),
        Offer.objects.create(
            buyer=user3,
            car=car3,
            max_price=Decimal("35000.00"),
            status=OfferStatus.PENDING,
        ),
        Offer.objects.create(
            buyer=user1,
            car=car3,
            max_price=Decimal("30000.00"),
            status=OfferStatus.REJECTED,
        ),
    ]

    return users, cars, offers


@pytest.mark.django_db
class TestOfferFiltering:
    def test_filter_offers_by_buyer_username(
        self,
        api_client: APIClient,
        test_data: tuple[list[User], list[Car], list[Offer]],
    ) -> None:
        users, _, _ = test_data
        response = api_client.get("/api/offers/", {"buyer": "john"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        for offer in response.data:
            assert offer["buyer"] == users[0].id

    def test_filter_offers_by_car_model(
        self,
        api_client: APIClient,
        test_data: tuple[list[User], list[Car], list[Offer]],
    ) -> None:
        _, cars, _ = test_data
        response = api_client.get("/api/offers/", {"car": "Camry"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["car"] == cars[0].id

    def test_filter_offers_by_status(
        self,
        api_client: APIClient,
        test_data: tuple[list[User], list[Car], list[Offer]],
    ) -> None:
        response = api_client.get("/api/offers/", {"status": "pending"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_filter_offers_by_max_price_range(
        self,
        api_client: APIClient,
        test_data: tuple[list[User], list[Car], list[Offer]],
    ) -> None:
        response = api_client.get(
            "/api/offers/", {"max_price_min": 25000, "max_price_max": 32000}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_case_insensitive_filters(
        self,
        api_client: APIClient,
        test_data: tuple[list[User], list[Car], list[Offer]],
    ) -> None:
        response = api_client.get("/api/offers/", {"buyer": "JOHN"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_multiple_status_filters(
        self,
        api_client: APIClient,
        test_data: tuple[list[User], list[Car], list[Offer]],
    ) -> None:
        response = api_client.get("/api/offers/", {"status": "rejected"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["status"] == "rejected"


@pytest.mark.django_db
class TestOfferSearch:
    def test_search_offers_by_buyer_username(
        self,
        api_client: APIClient,
        test_data: tuple[list[User], list[Car], list[Offer]],
    ) -> None:
        response = api_client.get("/api/offers/", {"search": "john"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_search_offers_by_car_model(
        self,
        api_client: APIClient,
        test_data: tuple[list[User], list[Car], list[Offer]],
    ) -> None:
        response = api_client.get("/api/offers/", {"search": "Series"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_search_offers_by_status(
        self,
        api_client: APIClient,
        test_data: tuple[list[User], list[Car], list[Offer]],
    ) -> None:
        response = api_client.get("/api/offers/", {"search": "accepted"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["status"] == "accepted"

    def test_empty_search_results(
        self,
        api_client: APIClient,
        test_data: tuple[list[User], list[Car], list[Offer]],
    ) -> None:
        response = api_client.get("/api/offers/", {"search": "nonexistent"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0


@pytest.mark.django_db
class TestOfferOrdering:
    def test_order_offers_by_max_price_asc(
        self,
        api_client: APIClient,
        test_data: tuple[list[User], list[Car], list[Offer]],
    ) -> None:
        response = api_client.get("/api/offers/", {"ordering": "max_price"})
        assert response.status_code == status.HTTP_200_OK
        prices = [float(offer["max_price"]) for offer in response.data]
        assert prices == sorted(prices)

    def test_order_offers_by_max_price_desc(
        self,
        api_client: APIClient,
        test_data: tuple[list[User], list[Car], list[Offer]],
    ) -> None:
        response = api_client.get("/api/offers/", {"ordering": "-max_price"})
        assert response.status_code == status.HTTP_200_OK
        prices = [float(offer["max_price"]) for offer in response.data]
        assert prices == sorted(prices, reverse=True)

    def test_default_ordering(
        self,
        api_client: APIClient,
        test_data: tuple[list[User], list[Car], list[Offer]],
    ) -> None:
        response = api_client.get("/api/offers/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 4


@pytest.mark.django_db
class TestCombinedFilterSearchOrder:
    def test_combined_filter_search_offers(
        self,
        api_client: APIClient,
        test_data: tuple[list[User], list[Car], list[Offer]],
    ) -> None:
        response = api_client.get(
            "/api/offers/",
            {"buyer": "john", "status": "pending", "ordering": "-max_price"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["max_price"] == "25000.00"

    def test_combined_price_range_and_search(
        self,
        api_client: APIClient,
        test_data: tuple[list[User], list[Car], list[Offer]],
    ) -> None:
        response = api_client.get(
            "/api/offers/",
            {
                "max_price_min": 20000,
                "max_price_max": 30000,
                "search": "pending",
                "ordering": "max_price",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        offer = response.data[0]
        assert offer["status"] == "pending"
        assert 20000 <= float(offer["max_price"]) <= 30000
