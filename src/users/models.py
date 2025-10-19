from typing import Any

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models

from core.abstract_models import TimeStampedModel
from users.validators import validate_positive_value


class UserManager(DjangoUserManager):
    def create_superuser(
        self,
        username: str,
        email: str | None = None,
        password: str | None = None,
        **extra_fields: Any,
    ) -> Any:
        extra_fields.setdefault("role", UserRoles.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return super().create_superuser(username, email, password, **extra_fields)


class UserRoles(models.TextChoices):
    ADMIN = "admin", ("Admin")
    BUYER = "buyer", ("Buyer")


class User(AbstractUser, TimeStampedModel):
    username = models.CharField(max_length=150, unique=True)  # type: ignore[misc]
    email = models.EmailField(unique=True)  # type: ignore[misc]
    role = models.CharField(
        max_length=20, choices=UserRoles.choices, default=UserRoles.BUYER
    )
    email_confirmed = models.BooleanField(default=False)

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"


class UserProfile(TimeStampedModel):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_profile"
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[validate_positive_value],
        help_text="Balance must be greater than 0",
    )
    total_spent = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[validate_positive_value],
        help_text="Balance must be greater than 0",
    )
    purchase_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self) -> str:
        return f"BuyerProfile({self.user.username})"
