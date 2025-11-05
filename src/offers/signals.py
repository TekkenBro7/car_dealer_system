from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from dealerships.models import DealershipSaleHistory
from offers.models import Offer, OfferStatus


# pylint: disable=unused-argument
@receiver(post_save, sender=Offer)
def create_dealership_sale_history(
    sender: type[Offer], instance: Offer, created: bool, **kwargs: Any
) -> None:
    # pylint: disable=no-member
    if created or instance.status != OfferStatus.ACCEPTED.value:
        return

    DealershipSaleHistory.objects.create(
        dealership=instance.dealership,
        car=instance.car,
        buyer=instance.buyer,
        price=instance.actual_price,
    )
