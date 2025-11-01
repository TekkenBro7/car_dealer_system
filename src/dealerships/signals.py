from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from dealerships.models import Inventory
from suppliers.models import SupplierOffer, SupplierSaleHistory


# pylint: disable=unused-argument
@receiver(post_save, sender=Inventory)
def create_supplier_sale_history(
    sender: type[Inventory], instance: Inventory, created: bool, **kwargs: Any
) -> None:
    if not created:
        return

    dealership = instance.dealership
    car = instance.car
    price = instance.price

    offer = SupplierOffer.objects.filter(car=car, price=price).first()
    if not offer:
        return

    SupplierSaleHistory.objects.create(
        supplier=offer.supplier,
        dealership=dealership,
        car=car,
        price=price,
        sale_date=timezone.now().date(),
    )
