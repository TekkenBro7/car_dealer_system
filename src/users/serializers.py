from typing import Any

from django.db.models import Sum
from rest_framework import serializers

from dealerships.models import DealershipSaleHistory
from users.models import User, UserProfile
from users.tasks import (
    send_confirmation_email_task,
    send_password_reset_email_task,
    send_username_change_email_task,
)
from users.utils import (
    email_verification,
    password_reset_verification,
    username_verification,
)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    is_active = serializers.BooleanField(default=True, initial=True)

    class Meta:
        model = User
        fields = ("username", "email", "password", "is_active")

    def create(self, validated_data: dict[str, Any]) -> User:
        user = User.objects.create_user(**validated_data)

        token = email_verification.generate_email_token(user)
        send_confirmation_email_task.delay(user.id, token)

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            "id",
            "balance",
            "total_spent",
            "purchase_count",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ["id", "created_at", "updated_at"]


class UserSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(read_only=True)
    email_confirmed = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "role",
            "email_confirmed",
            "user_profile",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_email(self, value: str) -> str:
        user = self.context["request"].user

        if value == user.email or User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        new_email = validated_data.get("email", instance.email)
        new_username = validated_data.get("username", instance.username)

        if new_email != instance.email:
            instance.email = new_email
            instance.email_confirmed = False

            token = email_verification.generate_email_token(instance)
            send_confirmation_email_task.delay(instance.id, token)

        if new_username != instance.username:
            token = username_verification.generate_username_token(
                instance, new_username
            )
            send_username_change_email_task.delay(instance.id, token, new_username)

        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=6)

    def validate_old_password(self, value: str) -> str:
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value: str) -> str:
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email not found.")
        return value

    def save(self, **kwargs: dict[str, Any]) -> User:
        email = self.validated_data["email"]
        user = User.objects.get(email=email)
        token = password_reset_verification.generate_password_reset_token(user)
        send_password_reset_email_task.delay(user.id, token)
        return user


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        user_id = password_reset_verification.verify_password_reset_token(
            attrs["token"]
        )
        if not user_id:
            raise serializers.ValidationError("Invalid or expired token.")
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise serializers.ValidationError("User not found.") from exc

        attrs["user"] = user
        return attrs

    def save(self, **kwargs: dict[str, Any]) -> User:
        user = self.validated_data["user"]
        new_password = self.validated_data["new_password"]
        user.set_password(new_password)
        user.save()
        return user


class BuyerReportSerializer(serializers.ModelSerializer):
    total_spent = serializers.SerializerMethodField()
    purchased_cars = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "total_spent", "purchased_cars"]

    def get_total_spent(self, obj: User) -> float:
        return (
            DealershipSaleHistory.objects.filter(buyer=obj).aggregate(
                total=Sum("price")
            )["total"]
            or 0
        )

    def get_purchased_cars(self, obj: User) -> list[str]:
        return list(
            DealershipSaleHistory.objects.filter(buyer=obj).values_list(
                "car__model_name", flat=True
            )
        )
