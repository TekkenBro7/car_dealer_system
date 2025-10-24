# pylint: disable=unused-argument
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from users.models import User, UserProfile, UserRoles


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


# pylint: disable=too-many-locals
@pytest.fixture
def test_users() -> list[User]:
    users = [
        User.objects.create_user(
            username="john_doe",
            email="john@example.com",
            password="pass123",
            email_confirmed=True,
        ),
        User.objects.create_user(
            username="jane_smith",
            email="jane@example.com",
            password="pass123",
            email_confirmed=False,
        ),
        User.objects.create_user(
            username="bob_wilson",
            email="bob@example.com",
            password="pass123",
            email_confirmed=True,
        ),
        User.objects.create_user(
            username="alice_brown",
            email="alice@example.com",
            password="pass123",
            email_confirmed=True,
        ),
    ]
    return users


@pytest.fixture
def test_profiles(test_users: list[User]) -> list[UserProfile]:
    profiles = []
    balances = [1000.00, 2500.50, 500.00, 750.25]
    total_spent = [5000.00, 12000.00, 2000.00, 3000.50]
    purchase_counts = [5, 12, 3, 8]

    for i, user in enumerate(test_users):
        profile = user.user_profile
        profile.balance = balances[i]
        profile.total_spent = total_spent[i]
        profile.purchase_count = purchase_counts[i]
        profile.save()
        profiles.append(profile)

    return profiles


@pytest.mark.django_db
class TestUserFiltering:
    def test_filter_users_by_username(
        self, api_client: APIClient, test_users: list[User]
    ) -> None:
        response = api_client.get("/api/users/", {"username": "john"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["username"] == "john_doe"

    def test_filter_users_by_email(
        self, api_client: APIClient, test_users: list[User]
    ) -> None:
        response = api_client.get("/api/users/", {"email": "jane"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["email"] == "jane@example.com"

    def test_filter_users_by_email_confirmed(
        self, api_client: APIClient, test_users: list[User]
    ) -> None:
        response = api_client.get("/api/users/", {"email_confirmed": "true"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_filter_users_by_email_not_confirmed(
        self, api_client: APIClient, test_users: list[User]
    ) -> None:
        response = api_client.get("/api/users/", {"email_confirmed": "false"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["email_confirmed"] is False


@pytest.mark.django_db
class TestUserSearch:
    def test_search_users_by_username(
        self, api_client: APIClient, test_users: list[User]
    ) -> None:
        response = api_client.get("/api/users/", {"search": "john"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["username"] == "john_doe"

    def test_search_users_by_email(
        self, api_client: APIClient, test_users: list[User]
    ) -> None:
        response = api_client.get("/api/users/", {"search": "example.com"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 4

    def test_search_users_case_insensitive(
        self, api_client: APIClient, test_users: list[User]
    ) -> None:
        response = api_client.get("/api/users/", {"search": "JOHN"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["username"] == "john_doe"


@pytest.mark.django_db
class TestUserOrdering:
    def test_order_users_by_username_asc(
        self, api_client: APIClient, test_users: list[User]
    ) -> None:
        response = api_client.get("/api/users/", {"ordering": "username"})
        assert response.status_code == status.HTTP_200_OK
        usernames = [user["username"] for user in response.data]
        assert usernames == sorted(usernames)

    def test_order_users_by_username_desc(
        self, api_client: APIClient, test_users: list[User]
    ) -> None:
        response = api_client.get("/api/users/", {"ordering": "-username"})
        assert response.status_code == status.HTTP_200_OK
        usernames = [user["username"] for user in response.data]
        assert usernames == sorted(usernames, reverse=True)


@pytest.mark.django_db
class TestUserProfileFiltering:
    def test_filter_profiles_by_balance_min(
        self, api_client: APIClient, test_profiles: list[UserProfile]
    ) -> None:
        response = api_client.get("/api/profiles/", {"balance_min": 1000})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_filter_profiles_by_balance_max(
        self, api_client: APIClient, test_profiles: list[UserProfile]
    ) -> None:
        response = api_client.get("/api/profiles/", {"balance_max": 800})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_filter_profiles_by_balance_range(
        self, api_client: APIClient, test_profiles: list[UserProfile]
    ) -> None:
        response = api_client.get(
            "/api/profiles/", {"balance_min": 500, "balance_max": 1000}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_filter_profiles_by_total_spent_max(
        self, api_client: APIClient, test_profiles: list[UserProfile]
    ) -> None:
        response = api_client.get("/api/profiles/", {"total_spent_max": 4000})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_filter_profiles_by_purchase_count_max(
        self, api_client: APIClient, test_profiles: list[UserProfile]
    ) -> None:
        response = api_client.get("/api/profiles/", {"purchase_count_max": 4})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1


@pytest.mark.django_db
class TestUserProfileSearch:
    def test_search_profiles_multiple_results(
        self, api_client: APIClient, test_profiles: list[UserProfile]
    ) -> None:
        response = api_client.get("/api/profiles/", {"search": "smith"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1


@pytest.mark.django_db
class TestUserProfileOrdering:
    def test_order_profiles_by_balance_asc(
        self, api_client: APIClient, test_profiles: list[UserProfile]
    ) -> None:
        response = api_client.get("/api/profiles/", {"ordering": "balance"})
        assert response.status_code == status.HTTP_200_OK
        balances = [float(profile["balance"]) for profile in response.data]
        assert balances == sorted(balances)

    def test_order_profiles_by_balance_desc(
        self, api_client: APIClient, test_profiles: list[UserProfile]
    ) -> None:
        response = api_client.get("/api/profiles/", {"ordering": "-balance"})
        assert response.status_code == status.HTTP_200_OK
        balances = [float(profile["balance"]) for profile in response.data]
        assert balances == sorted(balances, reverse=True)


@pytest.mark.django_db
class TestCombinedFilterSearchOrder:
    def test_combined_filter_search_users(
        self, api_client: APIClient, test_users: list[User]
    ) -> None:
        response = api_client.get(
            "/api/users/",
            {"role": UserRoles.BUYER, "search": "john", "ordering": "username"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["username"] == "john_doe"

    def test_combined_filter_order_profiles(
        self, api_client: APIClient, test_profiles: list[UserProfile]
    ) -> None:
        response = api_client.get(
            "/api/profiles/",
            {"balance_min": 500, "purchase_count_min": 5, "ordering": "-balance"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
