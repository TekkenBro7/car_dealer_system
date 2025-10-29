from unittest.mock import MagicMock, patch

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

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
def api_client(regular_user: User) -> APIClient:
    client = APIClient()
    refresh = RefreshToken.for_user(regular_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.mark.django_db
class TestUserViewSet:
    # pylint: disable=unused-argument
    def test_list_users(self, api_client: APIClient, regular_user: User) -> None:
        response = api_client.get("/api/users/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_retrieve_user(self, api_client: APIClient, regular_user: User) -> None:
        response = api_client.get(f"/api/users/{regular_user.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == regular_user.username
        assert response.data["email"] == regular_user.email

    @patch("users.serializers.send_confirmation_email")
    @patch("users.serializers.email_verification.generate_email_token")
    def test_create_user(
        self,
        mock_generate_token: MagicMock,
        mock_send_email: MagicMock,
        api_client: APIClient,
    ) -> None:
        mock_generate_token.return_value = "test-token"
        mock_send_email.return_value = None

        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123",
        }

        response = api_client.post("/api/users/", user_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["username"] == "newuser"
        assert response.data["email"] == "newuser@example.com"

        mock_send_email.assert_called_once()
        assert User.objects.filter(username="newuser").exists()

    @patch("users.serializers.send_username_change_email")
    @patch("users.serializers.username_verification.generate_username_token")
    def test_update_user(
        self,
        mock_generate_token: MagicMock,
        mock_send_email: MagicMock,
        api_client: APIClient,
        regular_user: User,
    ) -> None:
        mock_generate_token.return_value = "test-token"
        mock_send_email.return_value = None

        update_data = {"username": "updateduser"}
        response = api_client.patch(f"/api/users/{regular_user.id}/", update_data)
        assert response.status_code == status.HTTP_200_OK

        regular_user.refresh_from_db()
        assert regular_user.username == "testuser"

        mock_send_email.assert_called_once()

    def test_delete_user(self, api_client: APIClient, regular_user: User) -> None:
        response = api_client.delete(f"/api/users/{regular_user.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        assert not User.objects.filter(id=regular_user.id).exists()

    def test_create_user_invalid_data(self, api_client: APIClient) -> None:
        invalid_data = {
            "username": "newuser",
            "email": "invalid-email",
            "password": "123",
        }
        response = api_client.post("/api/users/", invalid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data


@pytest.mark.django_db
class TestUserProfileViewSet:
    # pylint: disable=unused-argument
    def test_list_profiles(self, api_client: APIClient, regular_user: User) -> None:
        response = api_client.get("/api/profiles/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_retrieve_profile(self, api_client: APIClient, regular_user: User) -> None:
        profile = regular_user.user_profile
        response = api_client.get(f"/api/profiles/{profile.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["balance"] == "0.00"
        assert response.data["purchase_count"] == 0

    def test_update_profile(self, api_client: APIClient, regular_user: User) -> None:
        profile = regular_user.user_profile
        update_data = {"balance": 1500.50, "total_spent": 500.25}
        response = api_client.patch(f"/api/profiles/{profile.id}/", update_data)
        assert response.status_code == status.HTTP_200_OK

        profile.refresh_from_db()
        assert profile.balance == 1500.50
        assert profile.total_spent == 500.25

    def test_create_profile_not_allowed(
        self, api_client: APIClient, regular_user: User
    ) -> None:
        profile_data = {
            "user": regular_user.id,
            "balance": 1000.00,
            "total_spent": 0.00,
            "purchase_count": 0,
        }
        response = api_client.post("/api/profiles/", profile_data)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_delete_profile_not_allowed(
        self, api_client: APIClient, regular_user: User
    ) -> None:
        profile_data = {"balance": 1000.00, "total_spent": 0.00, "purchase_count": 0}
        response = api_client.delete(f"/api/profiles/{regular_user.id}/", profile_data)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_update_profile_negative_balance(
        self, api_client: APIClient, regular_user: User
    ) -> None:
        profile = regular_user.user_profile
        update_data = {"balance": -100.00}
        response = api_client.patch(f"/api/profiles/{profile.id}/", update_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "balance" in response.data


@pytest.mark.django_db
class TestConfirmEmailView:
    @patch("users.services.email_service.email_verification.verify_email_token")
    def test_confirm_email_success(
        self, mock_verify_token: MagicMock, api_client: APIClient, regular_user: User
    ) -> None:
        mock_verify_token.return_value = regular_user.id

        response = api_client.get("/api/auth/confirm-email/valid-token/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "Email successfully confirmed."

        regular_user.refresh_from_db()
        assert regular_user.email_confirmed is True

    @patch("users.services.email_service.email_verification.verify_email_token")
    def test_confirm_email_invalid_token(
        self, mock_verify_token: MagicMock, api_client: APIClient
    ) -> None:
        mock_verify_token.return_value = None

        response = api_client.get("/api/auth/confirm-email/invalid-token/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "The link is invalid or outdated."

    @patch("users.services.email_service.email_verification.verify_email_token")
    def test_confirm_email_user_not_found(
        self, mock_verify_token: MagicMock, api_client: APIClient
    ) -> None:
        mock_verify_token.return_value = 99999

        response = api_client.get("/api/auth/confirm-email/valid-token/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["detail"] == "The user was not found."
