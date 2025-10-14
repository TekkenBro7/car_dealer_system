from django.contrib.auth import get_user_model
from django.db import models

from core.abstract_models import TimeStampedModel

User = get_user_model()


class OfferStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    CANCELLED = "cancelled", "Cancelled"


class Offer(TimeStampedModel):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="offers")
    car = models.ForeignKey("cars.car", on_delete=models.CASCADE)
    max_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=OfferStatus.choices, default=OfferStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Offer by {self.buyer.username} for {self.car.model_name} up to ${self.max_price}"
