from decimal import Decimal

from cars.models import Car
from core.logging import logger
from dealerships.models import Dealership, Inventory


def update_inventory(dealership: Dealership, car: Car, price: Decimal) -> None:
    """
    Increase inventory for given dealership and car

    If inventory record does not exist - create it with quantity 1
    If exists → increase quantity +1 and update latest purchase price

    This is used when dealership actually buys vehicle from suppliers
    """
    inventory, created = Inventory.objects.get_or_create(
        dealership=dealership,
        car=car,
        defaults={"quantity": 1, "price": price},
    )
    if not created:
        inventory.quantity += 1
        inventory.price = price
        inventory.save(update_fields=["quantity", "price"])

    logger.info("inventory updated: %s %s %s", dealership, car, price)
