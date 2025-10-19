from datetime import date
from decimal import Decimal
from typing import Union

from django.core.exceptions import ValidationError


def validate_positive_value(value: Union[int, float, Decimal]) -> None:
    if value <= 0:
        raise ValidationError(
            f"Price must be greater than 0. Got {value}.",
        )


def validate_founded_year(value: int) -> None:
    if value > date.today().year:
        raise ValidationError(f"Founded year cannot be in the future: {value}")
