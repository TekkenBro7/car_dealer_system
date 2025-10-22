from unittest.mock import MagicMock, patch

from django.test import TestCase

from users.models import User
from users.serializers import RegisterSerializer, UserProfileSerializer, UserSerializer


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
