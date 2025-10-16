from django.contrib.auth.models import AbstractUser
from django.db import models

from core.abstract_models import TimeStampedModel


class UserRoles(models.TextChoices):
    ADMIN = "admin", ("Admin")
    BUYER = "buyer", ("Buyer")


class User(AbstractUser, TimeStampedModel):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20, choices=UserRoles.choices, default=UserRoles.BUYER
    )
    email_confirmed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"


class UserProfile(TimeStampedModel):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_profile"
    )
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    purchase_count = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self) -> str:
        return f"BuyerProfile({self.user.username})"
