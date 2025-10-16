from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, UserProfile


# pylint: disable=unused-argument
@receiver(post_save, sender=User)
def create_buyer_profile(
    sender: type[User], instance: User, created: bool, **kwargs: Any
) -> None:
    if created:
        UserProfile.objects.create(user=instance)
