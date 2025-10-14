from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.abstract_models import TimeStampedModel

User = get_user_model()


class Supplier(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    country = models.CharField(max_length=2, blank=True)
    contact_email = models.EmailField(blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"

    def __str__(self) -> str:
        return self.name


class SupplierOffer(TimeStampedModel):
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="offers"
    )
    car = models.ForeignKey("cars.car", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "Supplier Offer"
        verbose_name_plural = "Supplier Offers"
        unique_together = ("supplier", "car")

    def __str__(self) -> str:
        return f"{self.supplier.name} offers {self.car} for ${self.price}"


class SupplierPromotion(TimeStampedModel):
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="promotions"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cars = models.ManyToManyField(
        "cars.Car", related_name="supplier_promotions", blank=True
    )
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
        verbose_name = "Supplier Promotion"
        verbose_name_plural = "Supplier Promotions"

    def __str__(self) -> str:
        return f"{self.title} @ {self.supplier.name} ({self.discount_percent}%)"


class SupplierSaleHistory(TimeStampedModel):
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="sales"
    )
    dealership = models.ForeignKey(
        "dealerships.Dealership", on_delete=models.SET_NULL, null=True, blank=True
    )
    car = models.ForeignKey("cars.Car", on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Supplier Sale History"
        verbose_name_plural = "Supplier Sales History"

    def __str__(self) -> str:
        return f"{self.supplier.name} -> {self.dealership or 'N/A'}: {self.car} ${self.price}"
