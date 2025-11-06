from celery import shared_task
from django.utils import timezone

from core.logging import logger
from dealerships.models import Dealership
from dealerships.services.autobuy import (
    execute_purchase,
    select_global_best_offer,
    select_history_best_offer,
    select_preferred_best_offer,
)


@shared_task
def auto_buy_from_suppliers() -> None:
    """
    Celery task that automatically purchases cars from suppliers for all active dealerships

    Logic:
      1) iterate through all active dealerships
      2) try to find the best offer for dealership's preferred models
      3) if nothing found - try based on dealership's own sales history
      4) if nothing found - fallback to global most popular models on platform
      5) if offer exists and dealership has enough balance - buy and update inventory and balance
    """
    logger.info("auto_buy_from_suppliers start")
    now = timezone.now().date()

    for d in Dealership.objects.filter(is_active=True):
        logger.info("[%s] dealership %s start", d.id, d.name)

        _, price, car = select_preferred_best_offer(d, now)
        if price is None or car is None:
            logger.info("[%s] no preferred offer found", d.id)

            _, price, car = select_history_best_offer(d, now)
            if price is None or car is None:
                logger.info("[%s] no history offer found", d.id)

                _, price, car = select_global_best_offer(now)
                if price is None or car is None:
                    logger.info("[%s] no global popular offers found", d.id)
                    continue

        if price > d.balance:
            logger.info("[%s] skipping, price %s > balance %s", d.id, price, d.balance)
            continue

        execute_purchase(d, car, price)
        logger.info("[%s] bought %s for %s", d.id, car, price)

    logger.info("auto_buy_from_suppliers end")
