from typing import Any

from rest_framework import serializers

from users.models import User, UserProfile
from users.services.email_service import send_confirmation_email
from users.utils import email_verification


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def create(self, validated_data: dict[str, Any]) -> User:
        user = User.objects.create_user(**validated_data)

        token = email_verification.generate_email_token(user)
        send_confirmation_email(user, token)

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("id", "balance", "total_spent", "purchase_count")


class UserSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(read_only=True)
    email_confirmed = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "role", "email_confirmed", "user_profile")
