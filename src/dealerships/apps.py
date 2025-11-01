from django.apps import AppConfig


class DealershipConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dealerships"

    def ready(self) -> None:
        import dealerships.signals  # noqa: F401
