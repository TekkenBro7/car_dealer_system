from datetime import date
from decimal import Decimal
from typing import Optional, Tuple

from django.db import transaction
from django.db.models import Count

from cars.models import Car
from dealerships.models import Dealership, DealershipSaleHistory
from dealerships.services.inventory import update_inventory
from dealerships.services.supplier_offers import find_best_offer_for_car
from suppliers.models import SupplierOffer


def _select_best_offer_for_car(
    car: Car, now: date
) -> Tuple[Optional[SupplierOffer], Optional[Decimal], Optional[Car]]:
    """
    For a given car returns best supplier offer (with promotions applied)

    Returns:
        tuple(SupplierOffer, Decimal, Car) or (None, None)
        Offer + final price + same car object returned
    """
    offer, price = find_best_offer_for_car(car, now)
    if offer:
        return offer, price, offer.car
    return None, None, None


def select_preferred_best_offer(
    d: Dealership, now: date
) -> Tuple[Optional[SupplierOffer], Optional[Decimal], Optional[Car]]:
    """
    Strategy #1:
    Try to buy among dealership "preferred models"

    For each preferred model - get best supplier price and pick the cheapest

    Returns:
        tuple(SupplierOffer, Decimal, Car) or (None, None, None)
    """
    best: Tuple[Optional[SupplierOffer], Optional[Decimal], Optional[Car]] = (
        None,
        None,
        None,
    )
    price_chosen: Optional[Decimal] = None

    for pm in d.preferred_models.select_related("car"):
        offer, price, car = _select_best_offer_for_car(pm.car, now)
        if price is None:
            continue

        if price <= d.balance and (price_chosen is None or price < price_chosen):
            best = (offer, price, car)
            price_chosen = price

    return best


def select_history_best_offer(
    d: Dealership, now: date
) -> Tuple[Optional[SupplierOffer], Optional[Decimal], Optional[Car]]:
    """
    Strategy #2:
    If no preferred models found - fallback to the most sold car in this dealership

    Returns:
        tuple(SupplierOffer, Decimal, Car) or (None, None, None)
    """
    top = (
        DealershipSaleHistory.objects.filter(dealership=d)
        .values("car")
        .annotate(cnt=Count("id"))
        .order_by("-cnt")
        .first()
    )
    if not top:
        return None, None, None

    car = Car.objects.get(id=top["car"])
    return _select_best_offer_for_car(car, now)


def select_global_best_offer(
    now: date,
) -> Tuple[Optional[SupplierOffer], Optional[Decimal], Optional[Car]]:
    """
    Strategy #3:
    If even dealership has no history - fallback to globally most sold car

    Returns:
        tuple(SupplierOffer, Decimal, Car) or (None, None, None)
    """
    top = (
        DealershipSaleHistory.objects.values("car")
        .annotate(cnt=Count("id"))
        .order_by("-cnt")
        .first()
    )
    if not top:
        return None, None, None

    car = Car.objects.get(id=top["car"])
    return _select_best_offer_for_car(car, now)


def execute_purchase(d: Dealership, car: Car, price: Decimal) -> None:
    with transaction.atomic():
        d.balance -= price
        d.save(update_fields=["balance"])
        update_inventory(d, car, price)
