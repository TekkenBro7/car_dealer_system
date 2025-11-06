from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

from cars.models import Car
from core.logging import logger
from suppliers.models import SupplierOffer, SupplierPromotion


def apply_supplier_promotion_price(offer: SupplierOffer, now_date: date) -> Decimal:
    """
    Apply active percentage promotions to supplier offer price

    Logic:
    - find all promotions active for this supplier on given date
    - accumulate discounts (only if promo applies to this car or to all cars)
    - discount capped at 100%
    - return final price with 2 decimal rounding
    """
    logger.info("Apply promo: %s", offer)

    promos = SupplierPromotion.objects.filter(
        supplier=offer.supplier,
        start_date__lte=now_date,
        end_date__gte=now_date,
    )

    price = offer.price
    total_discount = Decimal("0")

    for promo in promos:
        discount = Decimal(promo.discount_percent)
        if promo.cars.exists():
            if promo.cars.filter(pk=offer.car.pk).exists():
                total_discount += discount
        else:
            total_discount += discount

    total_discount = min(total_discount, Decimal("100"))

    price = (price * (Decimal("1") - total_discount / Decimal("100"))).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    logger.info("final price: %s", price)

    return price


def find_best_offer_for_car(
    car: Car, now_date: date
) -> tuple[Optional[SupplierOffer], Optional[Decimal]]:
    """
    Iterate all active supplier offers for given car
    and return (offer, final_price_after_promotions) for the lowest price
    applying promotions

    If there are no offers - return None
    """
    offers = SupplierOffer.objects.filter(
        car=car, is_active=True, supplier__is_active=True
    ).select_related("supplier")
    best_offer = None
    best_price = None

    for offer in offers:
        price = apply_supplier_promotion_price(offer, now_date)
        if best_price is None or price < best_price:
            best_offer = offer
            best_price = price

    if best_offer is not None and best_price:
        return best_offer, best_price

    return None, None
