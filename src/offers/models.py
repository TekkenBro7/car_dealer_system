from django.contrib.auth import get_user_model
from django.db import models

from cars.models import Car
from core.abstract_models import TimeStampedModel
from offers.validators import validate_positive_value

User = get_user_model()


class OfferStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    CANCELLED = "cancelled", "Cancelled"


class Offer(TimeStampedModel):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="offers")
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    max_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[validate_positive_value],
        help_text="Price must be greater than 0",
    )
    status = models.CharField(
        max_length=20, choices=OfferStatus.choices, default=OfferStatus.PENDING
    )

    def __str__(self) -> str:
        return f"Offer by {self.buyer.username} for {self.car.model_name} up to ${self.max_price}"
