from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

from cars.models import Car
from core.logging import logger
from dealerships.models import Dealership, DealershipPromotion


def apply_dealership_promotion_price(
    dealership: Dealership, car: Car, now: date
) -> Optional[Decimal]:
    """
    Calculate final price for a car in specific dealership,
    taking into account all active promotions for this dealership on current date

    If dealership does not have this car in inventory - return None
    """
    logger.info("Calc dealership promo price %s %s", dealership.id, car.id)

    inv = dealership.inventory.filter(car=car).first()
    if inv is None:
        return None

    base_price = inv.price

    promos = DealershipPromotion.objects.filter(
        dealership=dealership,
        start_date__lte=now,
        end_date__gte=now,
    )

    total_discount = Decimal("0")

    for promo in promos:
        d = promo.discount_percent
        if promo.cars.exists():
            if promo.cars.filter(pk=car.pk).exists():
                total_discount += d
        else:
            total_discount += d

    total_discount = min(total_discount, Decimal("100"))

    final_price = (base_price * (Decimal(1) - total_discount / Decimal(100))).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    logger.info("Final price = %s", final_price)
    return final_price
