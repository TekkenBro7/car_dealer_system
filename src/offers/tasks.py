from celery import shared_task
from django.utils import timezone

from core.logging import logger
from dealerships.models import Inventory
from offers.models import Offer, OfferStatus
from offers.services.dealership_offers import apply_dealership_promotion_price
from offers.services.purchase import execute_offer_purchase


@shared_task
def process_pending_offers() -> None:
    """
    Process pending buyer offers.
    For each Offer:
    - find dealerships having that car
    - calc final price with dealership discounts
    - if <= max_price and enough quantity + buyer has money -> accept + perform sale
    """
    logger.info("Process_pending_offers start")
    now = timezone.now().date()

    qs = Offer.objects.select_related("buyer", "car").filter(status=OfferStatus.PENDING)

    for offer in qs:
        buyer = offer.buyer
        car = offer.car

        logger.info(
            "Check offer #%s - buyer=%s car=%s",
            offer.id,
            buyer.username,
            car.model_name,
        )

        best = None
        best_price = None

        for inv in Inventory.objects.select_related("dealership").filter(
            car=car, quantity__gt=0
        ):
            p = apply_dealership_promotion_price(inv.dealership, car, now)
            if p is None:
                continue

            logger.info(
                "Dealership=%s base=%s final=%s", inv.dealership.name, inv.price, p
            )

            if p <= offer.max_price:
                if best_price is None or p < best_price:
                    best = (inv, p)
                    best_price = p

        if best is None:
            logger.info(
                "No suitable dealership found for offer #%s car=%s",
                offer.id,
                car.model_name,
            )
            continue

        inv, final_price = best
        profile = buyer.user_profile

        if profile.balance < final_price:
            logger.info("Buyer %s no money for %s", buyer.id, final_price)
            offer.status = OfferStatus.REJECTED
            offer.save(update_fields=["status"])
            continue

        success = execute_offer_purchase(offer, inv, final_price)
        if not success:
            offer.status = OfferStatus.REJECTED
            offer.save(update_fields=["status"])
            continue

        logger.info(
            "Offer %s accepted from dealership %s for %s",
            offer.id,
            inv.dealership.id,
            final_price,
        )

    logger.info("Process_pending_offers end")
