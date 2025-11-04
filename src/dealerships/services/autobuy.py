from datetime import date
from decimal import Decimal
from typing import Optional, Tuple

from django.db import transaction
from django.db.models import Count

from cars.models import Car
from dealerships.models import Dealership, DealershipSaleHistory
from dealerships.services.inventory import update_inventory
from dealerships.services.supplier_offers import find_best_offer_for_car


def _select_best_offer_for_car(car: Car, now: date) -> Optional[Tuple]:
    """
    For a given car returns best supplier offer (with promotions applied)

    Returns:
        tuple(SupplierOffer, Decimal, Car) or None
        Offer + final price + same car object returned
    """
    res = find_best_offer_for_car(car, now)
    if res:
        offer, price = res
        return offer, price, offer.car
    return None


def select_preferred_best_offer(d: Dealership, now: date) -> Optional[Tuple]:
    """
    Strategy #1:
    Try to buy among dealership "preferred models"

    For each preferred model - get best supplier price and pick the cheapest

    Returns:
        tuple(SupplierOffer, Decimal, Car) or None
    """
    best = None
    price_chosen: Optional[Decimal] = None

    for pm in d.preferred_models.select_related("car"):
        res = _select_best_offer_for_car(pm.car, now)
        if not res:
            continue

        _, price, _ = res
        if price <= d.balance and (price_chosen is None or price < price_chosen):
            best = res
            price_chosen = price

    return best


def select_history_best_offer(d: Dealership, now: date) -> Optional[Tuple]:
    """
    Strategy #2:
    If no preferred models found - fallback to the most sold car in this dealership

    Returns:
        tuple(SupplierOffer, Decimal, Car) or None
    """
    top = (
        DealershipSaleHistory.objects.filter(dealership=d)
        .values("car")
        .annotate(cnt=Count("id"))
        .order_by("-cnt")
        .first()
    )
    if not top:
        return None

    car = Car.objects.get(id=top["car"])
    return _select_best_offer_for_car(car, now)


def select_global_best_offer(now: date) -> Optional[Tuple]:
    """
    Strategy #3:
    If even dealership has no history - fallback to globally most sold car

    Returns:
        tuple(SupplierOffer, Decimal, Car) or None
    """
    top = (
        DealershipSaleHistory.objects.values("car")
        .annotate(cnt=Count("id"))
        .order_by("-cnt")
        .first()
    )
    if not top:
        return None

    car = Car.objects.get(id=top["car"])
    return _select_best_offer_for_car(car, now)


def execute_purchase(d: Dealership, car: Car, price: Decimal) -> None:
    with transaction.atomic():
        d.balance -= price
        d.save(update_fields=["balance"])
        update_inventory(d, car, price)
