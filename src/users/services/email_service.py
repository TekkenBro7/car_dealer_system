from typing import Any

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.response import Response

from core.logging import logger
from users.models import User
from users.utils import email_verification, username_verification


def send_confirmation(
    user: User, token: str, subject: str, template_name: str, context: dict[str, Any]
) -> None:
    """
    Universal email confirmation sender.
    """
    try:
        logger.info("Sending confirmation to %s", user)

        path = context.get("path", "")
        confirm_url = f"{settings.BACKEND_URL}/{path}/{token}/"
        context = {**context, "confirm_url": confirm_url}

        from_email = settings.DEFAULT_FROM_EMAIL
        to = [user.email]

        html_content = render_to_string(template_name, context)
        text_content = (
            f"Hello, {user.username}!\n\n"
            f"Please confirm by following the link: {confirm_url}"
        )

        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        logger.info("Email sent successfully to %s", user.email)
    except Exception as e:
        logger.error("Failed to send confirmation: %s", e, exc_info=True)


def send_confirmation_email(user: User, token: str) -> None:
    send_confirmation(
        user=user,
        token=token,
        subject="Confirmation of registration",
        template_name="emails/confirm_email.html",
        context={"username": user.username, "path": "api/auth/confirm-email"},
    )


def confirm_user_email(token: str) -> Response:
    """
    Validate the token, confirm user's email, and return appropriate Response.
    """
    user_pk = email_verification.verify_email_token(token)
    if not user_pk:
        return Response(
            {"detail": "The link is invalid or outdated."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = User.objects.get(pk=user_pk)
    except ObjectDoesNotExist:
        return Response(
            {"detail": "The user was not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    user.email_confirmed = True
    user.save()
    return Response(
        {"detail": "Email successfully confirmed."},
        status=status.HTTP_200_OK,
    )


def confirm_user_username(token: str) -> Response:
    """
    Validate the token, confirm user's username, and return appropriate Response.
    """
    user_id, new_username = username_verification.verify_username_token(token)
    if not user_id:
        return Response(
            {"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(pk=user_id)
    except ObjectDoesNotExist:
        return Response(
            {"detail": "The user was not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    user.username = new_username  # type: ignore[assignment]
    user.save()

    return Response(
        {"detail": "Username successfully updated."}, status=status.HTTP_200_OK
    )


def send_username_change_email(user: User, token: str, new_username: str) -> None:
    send_confirmation(
        user=user,
        token=token,
        subject="Confirm your username change",
        template_name="emails/confirm_username.html",
        context={
            "username": user.username,
            "new_username": new_username,
            "path": "api/auth/confirm-username",
        },
    )


def send_password_reset_email(user: User, token: str) -> None:
    send_confirmation(
        user=user,
        token=token,
        subject="Reset your password",
        template_name="emails/password_reset.html",
        context={"username": user.username, "path": "api/auth/reset-password"},
    )
