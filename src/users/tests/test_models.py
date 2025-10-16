from typing import Any

from django.db import IntegrityError
from django.test import TestCase

from users.models import User, UserProfile, UserRoles
from users.signals import create_buyer_profile


class UserModelTest(TestCase):
    def setUp(self) -> None:
        self.user_data: dict[str, Any] = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
        }

    def test_user_creation(self) -> None:
        user = User.objects.create_user(**self.user_data)

        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.role, UserRoles.BUYER)
        self.assertFalse(user.email_confirmed)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_user_string_representation(self) -> None:
        user = User.objects.create_user(**self.user_data)

        expected_str = f"{user.username} ({user.role})"
        self.assertEqual(str(user), expected_str)

    def test_user_role_choices(self) -> None:
        role_choices = dict(UserRoles.choices)
        self.assertIn("admin", role_choices)
        self.assertIn("buyer", role_choices)
        self.assertEqual(role_choices["admin"], "Admin")
        self.assertEqual(role_choices["buyer"], "Buyer")

    def test_user_unique_username(self) -> None:
        User.objects.create_user(**self.user_data)

        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="testuser",
                email="different@example.com",
                password="testpass123",
            )

    def test_user_unique_email(self) -> None:
        User.objects.create_user(**self.user_data)

        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="differentuser",
                email="test@example.com",
                password="testpass123",
            )

    def test_user_admin_role(self) -> None:
        admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
            role=UserRoles.ADMIN,
        )

        self.assertEqual(admin_user.role, UserRoles.ADMIN)

    def test_create_superuser(self) -> None:
        superuser = User.objects.create_superuser(
            username="superuser", email="super@example.com", password="superpass123"
        )

        self.assertEqual(superuser.username, "superuser")
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertEqual(superuser.role, UserRoles.ADMIN)


class UserProfileModelTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.user_profile = UserProfile.objects.get(user=self.user)

    def test_user_profile_creation(self) -> None:
        self.assertEqual(self.user_profile.user, self.user)
        self.assertEqual(self.user_profile.balance, 0)
        self.assertEqual(self.user_profile.total_spent, 0)
        self.assertEqual(self.user_profile.purchase_count, 0)
        self.assertTrue(self.user_profile.is_active)
        self.assertIsNotNone(self.user_profile.created_at)
        self.assertIsNotNone(self.user_profile.updated_at)

    def test_user_profile_string_representation(self) -> None:
        expected_str = f"BuyerProfile({self.user.username})"
        self.assertEqual(str(self.user_profile), expected_str)

    def test_user_profile_one_to_one_relationship(self) -> None:
        self.assertEqual(self.user_profile.user, self.user)
        self.assertEqual(self.user.user_profile, self.user_profile)  # type: ignore

    def test_user_profile_decimal_fields(self) -> None:
        self.user_profile.balance = 1500.75
        self.user_profile.total_spent = 5000.25
        self.user_profile.save()

        self.assertEqual(float(self.user_profile.balance), 1500.75)
        self.assertEqual(float(self.user_profile.total_spent), 5000.25)


class SignalTest(TestCase):
    def test_signal_function_directly(self) -> None:
        user = User.objects.create_user(
            username="directuser", email="direct@example.com", password="directpass123"
        )

        UserProfile.objects.filter(user=user).delete()
        self.assertFalse(UserProfile.objects.filter(user=user).exists())

        create_buyer_profile(sender=User, instance=user, created=True)

        self.assertTrue(UserProfile.objects.filter(user=user).exists())
