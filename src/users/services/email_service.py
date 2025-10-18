from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.response import Response

from core.logging import logger
from users.models import User
from users.utils import email_verification


def send_confirmation_email(user: User, token: str) -> None:
    """
    Send an email confirmation message with an activation link to the user int html format.

    Args:
        user (User): The user instance to send the email to.
        token (str): The generated email confirmation token.
    """
    try:
        logger.info("Sending email to %s to verify email", user)

        confirm_url = f"{settings.BACKEND_URL}/api/confirm-email/{token}/"

        subject = "Confirmation of registration"
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [user.email]

        html_content = render_to_string(
            "emails/confirm_email.html",
            {"username": user.username, "confirm_url": confirm_url},
        )
        text_content = (
            f"Hello, {user.username}!\n\n"
            f"Confirm your email by following the link: {confirm_url}"
        )

        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        logger.info("Email sent successfully to %s email %s", user, to)
    except Exception as e:
        logger.error("Failed to send email: %s", e, exc_info=True)


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
