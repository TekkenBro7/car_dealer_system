from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from core.logging import logger
from users.models import User


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
