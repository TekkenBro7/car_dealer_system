from typing import Any
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


@pytest.fixture
def unauthenticated_client() -> APIClient:
    return APIClient()


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


@pytest.mark.django_db
class TestConfirmUsernameView:
    @patch("users.services.email_service.username_verification.verify_username_token")
    def test_confirm_username_success(
        self, mock_verify_token: MagicMock, api_client: APIClient, regular_user: User
    ) -> None:
        mock_verify_token.return_value = (regular_user.id, "newusername")

        response = api_client.get("/api/auth/confirm-username/valid-token/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "Username successfully updated."

        regular_user.refresh_from_db()
        assert regular_user.username == "newusername"

    @patch("users.services.email_service.username_verification.verify_username_token")
    def test_confirm_username_invalid_token(
        self, mock_verify_token: MagicMock, api_client: APIClient
    ) -> None:
        mock_verify_token.return_value = (None, None)

        response = api_client.get("/api/auth/confirm-username/invalid-token/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Invalid or expired token."

    @patch("users.services.email_service.username_verification.verify_username_token")
    def test_confirm_username_user_not_found(
        self, mock_verify_token: MagicMock, api_client: APIClient
    ) -> None:
        mock_verify_token.return_value = (99999, "newusername")

        response = api_client.get("/api/auth/confirm-username/valid-token/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["detail"] == "The user was not found."


@pytest.mark.django_db
class TestChangePasswordView:
    def test_change_password_success(
        self, api_client: APIClient, regular_user: User
    ) -> None:
        data = {"old_password": "testpass123", "new_password": "newpassword456"}

        response = api_client.post("/api/auth/change-password/", data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["OK"] == "Password changed successfully."

        regular_user.refresh_from_db()
        assert regular_user.check_password("newpassword456")

    # pylint: disable=unused-argument
    def test_change_password_wrong_old_password(
        self, api_client: APIClient, regular_user: User
    ) -> None:
        data = {"old_password": "wrongpassword", "new_password": "newpassword456"}

        response = api_client.post("/api/auth/change-password/", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "old_password" in response.data

    # pylint: disable=unused-argument
    def test_change_password_missing_fields(
        self, api_client: APIClient, regular_user: User
    ) -> None:
        data = {"old_password": "testpass123"}

        response = api_client.post("/api/auth/change-password/", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "new_password" in response.data


@pytest.mark.django_db
class TestPasswordResetRequestView:
    # pylint: disable=unused-argument
    @patch("users.serializers.send_password_reset_email")
    @patch(
        "users.serializers.password_reset_verification.generate_password_reset_token"
    )
    def test_password_reset_request_success(
        self,
        mock_generate_token: MagicMock,
        mock_send_email: MagicMock,
        unauthenticated_client: APIClient,
        regular_user: User,
    ) -> None:
        mock_generate_token.return_value = "test-token"
        mock_send_email.return_value = None
        data = {"email": "test@example.com"}

        response = unauthenticated_client.post(
            "/api/auth/reset-password-request/", data
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["OK"] == "Password reset link sent to your email."
        mock_send_email.assert_called_once()

    def test_password_reset_request_nonexistent_email(
        self, unauthenticated_client: APIClient
    ) -> None:
        data = {"email": "nonexistent@example.com"}

        response = unauthenticated_client.post(
            "/api/auth/reset-password-request/", data
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_password_reset_request_missing_email(
        self, unauthenticated_client: APIClient
    ) -> None:
        data: dict[str, Any] = {}

        response = unauthenticated_client.post(
            "/api/auth/reset-password-request/", data
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data


@pytest.mark.django_db
class TestPasswordResetConfirmView:
    @patch("users.serializers.password_reset_verification.verify_password_reset_token")
    def test_password_reset_confirm_success(
        self,
        mock_verify_token: MagicMock,
        unauthenticated_client: APIClient,
        regular_user: User,
    ) -> None:
        mock_verify_token.return_value = regular_user.id
        data = {"token": "valid-reset-token", "new_password": "newpassword123"}

        response = unauthenticated_client.post("/api/auth/reset-password/", data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["OK"] == "Password successfully reset."

        regular_user.refresh_from_db()
        assert regular_user.check_password("newpassword123")

    @patch("users.serializers.password_reset_verification.verify_password_reset_token")
    def test_password_reset_confirm_invalid_token(
        self, mock_verify_token: MagicMock, unauthenticated_client: APIClient
    ) -> None:
        mock_verify_token.return_value = None
        data = {"token": "invalid-token", "new_password": "newpassword123"}

        response = unauthenticated_client.post("/api/auth/reset-password/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data

    @patch("users.serializers.password_reset_verification.verify_password_reset_token")
    def test_password_reset_confirm_user_not_found(
        self, mock_verify_token: MagicMock, unauthenticated_client: APIClient
    ) -> None:
        mock_verify_token.return_value = 99999
        data = {"token": "valid-token", "new_password": "newpassword123"}

        response = unauthenticated_client.post("/api/auth/reset-password/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data

    def test_password_reset_confirm_missing_fields(
        self, unauthenticated_client: APIClient
    ) -> None:
        data = {"token": "valid-token"}

        response = unauthenticated_client.post("/api/auth/reset-password/", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "new_password" in response.data
