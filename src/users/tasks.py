from celery import shared_task

from users.models import User
from users.services.email_service import (
    send_confirmation_email,
    send_password_reset_email,
    send_username_change_email,
)


@shared_task
def send_confirmation_email_task(user_id: int, token: str) -> None:
    user = User.objects.get(pk=user_id)
    send_confirmation_email(user, token)


@shared_task
def send_password_reset_email_task(user_id: int, token: str) -> None:
    user = User.objects.get(pk=user_id)
    send_password_reset_email(user, token)


@shared_task
def send_username_change_email_task(
    user_id: int, token: str, new_username: str
) -> None:
    user = User.objects.get(pk=user_id)
    send_username_change_email(user, token, new_username)
