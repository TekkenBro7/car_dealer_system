from decimal import Decimal
from typing import Union

from django.core.exceptions import ValidationError


def validate_positive_value(value: Union[int, float, Decimal]) -> None:
    if value <= 0:
        raise ValidationError(
            f"Price must be greater than 0. Got {value}.",
        )
