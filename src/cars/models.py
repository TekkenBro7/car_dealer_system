from django.db import models

from core.abstract_models import TimeStampedModel


class CarBrand(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = "Car Brand"
        verbose_name_plural = "Car Brands"

    def __str__(self) -> str:
        return self.name


class BodyType(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Body Type"
        verbose_name_plural = "Body Types"

    def __str__(self) -> str:
        return self.name


class Car(TimeStampedModel):
    brand = models.ForeignKey(CarBrand, on_delete=models.CASCADE, related_name="models")
    body_type = models.ForeignKey(
        BodyType, on_delete=models.SET_NULL, null=True, blank=True
    )
    model_name = models.CharField(max_length=150)

    class Meta:
        verbose_name = "Car Model"
        verbose_name_plural = "Car Models"
        unique_together = ("brand", "model_name")

    def __str__(self) -> str:
        return f"{self.brand.name} {self.model_name}"
