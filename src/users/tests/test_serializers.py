from unittest.mock import MagicMock, patch

from django.test import TestCase

from users.models import User
from users.serializers import (
    ChangePasswordSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    UserProfileSerializer,
    UserSerializer,
)


class TestRegisterSerializer(TestCase):
    def setUp(self) -> None:
        self.valid_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123",
        }

    def test_valid_serializer_data(self) -> None:
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_password_min_length_validation(self) -> None:
        invalid_data = self.valid_data.copy()
        invalid_data["password"] = "short"

        serializer = RegisterSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_required_fields(self) -> None:
        for field in ["username", "email", "password"]:
            invalid_data = self.valid_data.copy()
            del invalid_data[field]

            serializer = RegisterSerializer(data=invalid_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn(field, serializer.errors)

    @patch("users.serializers.send_confirmation_email")
    @patch("users.serializers.email_verification.generate_email_token")
    def test_create_user_calls_email_service(
        self, mock_generate_token: MagicMock, mock_send_email: MagicMock
    ) -> None:
        mock_generate_token.return_value = "mock_token"
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()

        self.assertIsInstance(user, User)
        self.assertEqual(user.username, self.valid_data["username"])
        self.assertEqual(user.email, self.valid_data["email"])
        self.assertTrue(user.check_password(self.valid_data["password"]))

        mock_generate_token.assert_called_once_with(user)
        mock_send_email.assert_called_once_with(user, "mock_token")

    def test_register_serializer_does_not_return_password(self) -> None:
        user = User.objects.create_user(**self.valid_data)
        serializer = RegisterSerializer(instance=user)
        self.assertNotIn("password", serializer.data)
        self.assertIn("email", serializer.data)

    def test_email_format_validation(self) -> None:
        invalid_data = self.valid_data.copy()
        invalid_data["email"] = "invalid-email"

        serializer = RegisterSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_unique_username_validation(self) -> None:
        User.objects.create_user(
            username="testuser", email="existing@example.com", password="testpass123"
        )

        serializer = RegisterSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)

    def test_unique_email_validation(self) -> None:
        User.objects.create_user(
            username="existinguser", email="test@example.com", password="testpass123"
        )

        serializer = RegisterSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)


class TestUserProfileSerializer(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.profile = self.user.user_profile

    def test_user_profile_serializer_fields(self) -> None:
        serializer = UserProfileSerializer(instance=self.profile)

        expected_fields = {
            "id",
            "balance",
            "total_spent",
            "purchase_count",
            "is_active",
            "created_at",
            "updated_at",
        }

        self.assertEqual(serializer.data.keys(), expected_fields)

    def test_read_only_fields(self) -> None:
        data = {"id": 999, "balance": 1000.00, "total_spent": 500.00}

        serializer = UserProfileSerializer(
            instance=self.profile, data=data, partial=True
        )
        self.assertTrue(serializer.is_valid())

        updated_profile = serializer.save()
        self.assertNotEqual(updated_profile.id, 999)
        self.assertEqual(updated_profile.balance, 1000)

    def test_balance_validation(self) -> None:
        data = {"balance": -100.00}

        serializer = UserProfileSerializer(
            instance=self.profile, data=data, partial=True
        )
        self.assertFalse(serializer.is_valid())

    def test_decimal_precision(self) -> None:
        data = {"balance": "1000.123", "total_spent": "500.456"}

        serializer = UserProfileSerializer(
            instance=self.profile, data=data, partial=True
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("balance", serializer.errors)
        self.assertIn("total_spent", serializer.errors)


class TestUserSerializer(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_user_serializer_includes_user_profile(self) -> None:
        serializer = UserSerializer(instance=self.user)
        data = serializer.data

        self.assertIn("user_profile", data)
        self.assertIn("email_confirmed", data)
        self.assertEqual(data["username"], "testuser")
        self.assertIn("balance", data["user_profile"])

    def test_email_confirmed_field(self) -> None:
        serializer = UserSerializer(instance=self.user)
        self.assertIn("email_confirmed", serializer.data)
        self.assertIsInstance(serializer.data["email_confirmed"], bool)
        self.assertEqual(serializer.data["email_confirmed"], False)


class TestChangePasswordSerializer(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="oldpassword123"
        )
        self.valid_data = {
            "old_password": "oldpassword123",
            "new_password": "newpassword456",
        }

    def test_valid_data(self) -> None:
        mock_request = MagicMock()
        mock_request.user = self.user

        serializer = ChangePasswordSerializer(
            data=self.valid_data, context={"request": mock_request}
        )
        self.assertTrue(serializer.is_valid())

    def test_old_password_validation_correct(self) -> None:
        mock_request = MagicMock()
        mock_request.user = self.user

        serializer = ChangePasswordSerializer(
            data=self.valid_data, context={"request": mock_request}
        )
        serializer.is_valid()

        validated_value = serializer.validate_old_password("oldpassword123")
        self.assertEqual(validated_value, "oldpassword123")

    def test_old_password_validation_incorrect(self) -> None:
        mock_request = MagicMock()
        mock_request.user = self.user

        invalid_data = {
            "old_password": "wrongpassword",
            "new_password": "newpassword456",
        }

        serializer = ChangePasswordSerializer(
            data=invalid_data, context={"request": mock_request}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("old_password", serializer.errors)
        self.assertEqual(
            str(serializer.errors["old_password"][0]), "Old password is incorrect."
        )

    def test_required_fields(self) -> None:
        mock_request = MagicMock()
        mock_request.user = self.user

        for field in ["old_password", "new_password"]:
            invalid_data = self.valid_data.copy()
            del invalid_data[field]

            serializer = ChangePasswordSerializer(
                data=invalid_data, context={"request": mock_request}
            )
            self.assertFalse(serializer.is_valid())
            self.assertIn(field, serializer.errors)


class TestPasswordResetRequestSerializer(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.valid_data = {"email": "test@example.com"}

    def test_valid_data(self) -> None:
        serializer = PasswordResetRequestSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_email_validation_existing_user(self) -> None:
        serializer = PasswordResetRequestSerializer(data=self.valid_data)
        serializer.is_valid()

        validated_value = serializer.validate_email("test@example.com")
        self.assertEqual(validated_value, "test@example.com")

    def test_email_validation_non_existing_user(self) -> None:
        invalid_data = {"email": "nonexistent@example.com"}

        serializer = PasswordResetRequestSerializer(data=invalid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
        self.assertEqual(
            str(serializer.errors["email"][0]), "User with this email not found."
        )

    @patch("users.serializers.send_password_reset_email")
    @patch(
        "users.serializers.password_reset_verification.generate_password_reset_token"
    )
    def test_save_method(
        self, mock_generate_token: MagicMock, mock_send_email: MagicMock
    ) -> None:
        mock_generate_token.return_value = "mock_reset_token"
        mock_send_email.return_value = None

        serializer = PasswordResetRequestSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

        result_user = serializer.save()

        self.assertEqual(result_user, self.user)
        mock_generate_token.assert_called_once_with(self.user)
        mock_send_email.assert_called_once_with(self.user, "mock_reset_token")

    def test_required_email_field(self) -> None:
        serializer = PasswordResetRequestSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)


class TestPasswordResetConfirmSerializer(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="oldpassword123"
        )
        self.valid_data = {
            "token": "valid_reset_token",
            "new_password": "newpassword456",
        }

    @patch("users.serializers.password_reset_verification.verify_password_reset_token")
    def test_valid_data(self, mock_verify_token: MagicMock) -> None:
        mock_verify_token.return_value = self.user.id

        serializer = PasswordResetConfirmSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    @patch("users.serializers.password_reset_verification.verify_password_reset_token")
    def test_validate_method_success(self, mock_verify_token: MagicMock) -> None:
        mock_verify_token.return_value = self.user.id

        serializer = PasswordResetConfirmSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

        validated_data = serializer.validate(self.valid_data)
        self.assertIn("user", validated_data)
        self.assertEqual(validated_data["user"], self.user)
        self.assertEqual(validated_data["token"], "valid_reset_token")
        self.assertEqual(validated_data["new_password"], "newpassword456")

    @patch("users.serializers.password_reset_verification.verify_password_reset_token")
    def test_validate_method_invalid_token(self, mock_verify_token: MagicMock) -> None:
        mock_verify_token.return_value = None

        serializer = PasswordResetConfirmSerializer(data=self.valid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
        self.assertEqual(
            str(serializer.errors["non_field_errors"][0]), "Invalid or expired token."
        )

    @patch("users.serializers.password_reset_verification.verify_password_reset_token")
    def test_validate_method_user_not_found(self, mock_verify_token: MagicMock) -> None:
        mock_verify_token.return_value = 99999

        serializer = PasswordResetConfirmSerializer(data=self.valid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
        self.assertEqual(
            str(serializer.errors["non_field_errors"][0]), "User not found."
        )

    def test_required_fields(self) -> None:
        for field in ["token", "new_password"]:
            invalid_data = self.valid_data.copy()
            del invalid_data[field]

            serializer = PasswordResetConfirmSerializer(data=invalid_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn(field, serializer.errors)

    @patch("users.serializers.password_reset_verification.verify_password_reset_token")
    def test_save_method(self, mock_verify_token: MagicMock) -> None:
        mock_verify_token.return_value = self.user.id

        serializer = PasswordResetConfirmSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

        result_user = serializer.save()

        self.assertEqual(result_user, self.user)

        self.user.refresh_from_db()

        self.assertTrue(self.user.check_password("newpassword456"))

    def test_write_only_new_password_field(self) -> None:
        serializer = PasswordResetConfirmSerializer()
        new_password_field = serializer.fields["new_password"]
        self.assertTrue(new_password_field.write_only)
