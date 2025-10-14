from typing import Any

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg, Count, Min, QuerySet, Sum
from django_countries.fields import CountryField

from cars.models import Car
from core.abstract_models import TimeStampedModel
from suppliers.models import SupplierOffer

User = get_user_model()


class Dealership(TimeStampedModel):
    name = models.CharField(max_length=255)
    country = CountryField()
    city = models.CharField(max_length=255, blank=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = "Dealership"
        verbose_name_plural = "Dealerships"

    def __str__(self) -> str:
        return self.name

    def get_best_suppliers(self) -> dict[str, dict[str, Any]]:
        best_offers = (
            SupplierOffer.objects.filter(is_active=True, supplier__is_active=True)
            .values("car__model_name")
            .annotate(best_price=Min("price"))
        )

        result = {}
        for offer in best_offers:
            car_name = offer["car__model_name"]
            best_price = offer["best_price"]

            best_supplier = (
                SupplierOffer.objects.filter(
                    car__model_name=car_name,
                    price=best_price,
                    is_active=True,
                    supplier__is_active=True,
                )
                .select_related("supplier")
                .first()
            )

            if best_supplier:
                result[car_name] = {
                    "supplier": best_supplier.supplier.name,
                    "price": best_supplier.price,
                }

        return result

    def get_unique_buyers(self) -> QuerySet:
        return self.sales_history.all().values("buyer__username").distinct()  # type: ignore

    def get_buyer_statistics(self) -> QuerySet:
        return (
            self.sales_history.all()  # type: ignore
            .values("buyer__username")
            .annotate(
                total_purchases=Count("id"),
                total_spent=Sum("price"),
                avg_price=Avg("price"),
            )
            .order_by("-total_spent")
        )


class Inventory(models.Model):
    dealership = models.ForeignKey(
        Dealership, on_delete=models.CASCADE, related_name="inventory"
    )
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Inventory"
        verbose_name_plural = "Inventories"

    def __str__(self) -> str:
        return f"{self.dealership.name}: {self.car.model_name} ({self.quantity})"


class PreferredModel(models.Model):
    dealership = models.ForeignKey(
        Dealership, on_delete=models.CASCADE, related_name="preferred_models"
    )
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    reason = models.TextField(blank=True, help_text="Why choose this model")

    class Meta:
        verbose_name = "Preffered Model"
        verbose_name_plural = "Preffered Models"

    def __str__(self) -> str:
        return f"{self.dealership.name} — {self.car.model_name}"


class DealershipPromotion(models.Model):
    dealership = models.ForeignKey(
        Dealership, on_delete=models.CASCADE, related_name="promotions"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cars = models.ManyToManyField(Car, related_name="dealership_promotions", blank=True)
    discount_percent = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Discount rate from 0 to 100",
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    class Meta:
        verbose_name = "Dealership Promotion"
        verbose_name_plural = "Dealership Promotions"

    def __str__(self) -> str:
        return f"{self.title} @ {self.dealership.name} ({self.discount_percent}%)"


class DealershipSaleHistory(models.Model):
    dealership = models.ForeignKey(
        Dealership, on_delete=models.CASCADE, related_name="sales_history"
    )
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Dealership Sale History"
        verbose_name_plural = "Dealership Sales History"

    def __str__(self) -> str:
        return f"{self.dealership.name} sold {self.car.model_name} to {self.buyer.username}"
