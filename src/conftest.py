from typing import Generator

import pytest
from django.test.utils import override_settings


@pytest.fixture(autouse=True)
def disable_cache_for_tests() -> Generator[None, None, None]:
    with override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.dummy.DummyCache",
            }
        },
    ):
        yield
