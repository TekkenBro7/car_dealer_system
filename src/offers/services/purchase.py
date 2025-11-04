from decimal import Decimal

from django.db import transaction

from core.logging import logger
from dealerships.models import Inventory
from offers.models import Offer, OfferStatus


def execute_offer_purchase(
    offer: Offer,
    inv: Inventory,
    final_price: Decimal,
) -> bool:
    """
    Atomically performs purchase for offer:
      - decrease inventory
      - write price to offer
      - update buyer profile
    return True if success, False if not enough balance
    """
    profile = offer.buyer.user_profile

    if profile.balance < final_price:
        logger.info(
            "[Offer=%s] insufficient funds, balance=%s price=%s",
            offer.id,
            profile.balance,
            final_price,
        )
        return False

    with transaction.atomic():
        inv.quantity -= 1
        inv.save(update_fields=["quantity"])

        if profile.balance < final_price:
            logger.info(
                "[Offer=%s] insufficient funds inside txn, balance=%s price=%s",
                offer.id,
                profile.balance,
                final_price,
            )
            transaction.set_rollback(True)
            return False

        profile.balance -= final_price
        profile.total_spent += final_price
        profile.purchase_count += 1
        profile.save(update_fields=["balance", "total_spent", "purchase_count"])

        offer.dealership = inv.dealership
        offer.actual_price = final_price
        offer.status = OfferStatus.ACCEPTED
        offer.save(update_fields=["dealership", "status", "actual_price"])

    return True
