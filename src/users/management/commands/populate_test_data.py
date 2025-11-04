import random
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from django.core.management.base import BaseCommand

from cars.models import BodyType, Car, CarBrand
from core.logging import logger
from dealerships.models import Dealership, Inventory, PreferredModel
from offers.models import Offer
from suppliers.models import Supplier, SupplierOffer, SupplierPromotion
from users.models import User


class Command(BaseCommand):
    help = "Populate the database with test data"

    def handle(self, *args: Any, **options: Any) -> None:
        self.clear_db()
        self.create_test_data()

    def clear_db(self) -> None:
        logger.info("Clearing database...")
        Offer.objects.all().delete()
        Inventory.objects.all().delete()
        PreferredModel.objects.all().delete()
        SupplierPromotion.objects.all().delete()
        SupplierOffer.objects.all().delete()
        Dealership.objects.all().delete()
        Supplier.objects.all().delete()
        Car.objects.all().delete()
        CarBrand.objects.all().delete()
        BodyType.objects.all().delete()
        User.objects.all().delete()
        logger.info("Database cleared!")

    def create_test_data(self) -> None:
        logger.info("Creating test data...")

        User.objects.create_superuser(
            username="admin", email="admin@test.com", password="admin"
        )
        buyers = [
            User.objects.create_user(
                username=f"buyer{i}", email=f"buyer{i}@test.com", password="buyer"
            )
            for i in range(1, 4)
        ]
        for buyer in buyers:
            profile = buyer.user_profile
            profile.balance = Decimal(random.randint(50_000, 200_000))
            profile.save(update_fields=["balance"])

        brands = [
            CarBrand.objects.create(name=name, country="US")
            for name in ["Tesla", "Toyota", "BMW"]
        ]
        bodies = [
            BodyType.objects.create(name=name) for name in ["Sedan", "SUV", "Hatchback"]
        ]

        cars = []
        for brand in brands:
            for i in range(1, 4):
                car = Car.objects.create(
                    brand=brand,
                    body_type=random.choice(bodies),
                    model_name=f"{brand.name} Model {i}",
                )
                cars.append(car)

        suppliers = []
        for i in range(1, 4):
            supplier = Supplier.objects.create(
                name=f"Supplier {i}",
                country="US",
                founded_year=2000 + i,
                contact_email=f"supplier{i}@test.com",
            )
            suppliers.append(supplier)

        for supplier in suppliers:
            for car in cars:
                price = Decimal(random.randint(20000, 500000))
                SupplierOffer.objects.create(supplier=supplier, car=car, price=price)

        for supplier in suppliers:
            promo = SupplierPromotion.objects.create(
                supplier=supplier,
                title=f"Promo {supplier.name}",
                discount_percent=random.choice([5, 10, 15]),
                start_date=date.today() - timedelta(days=2),
                end_date=date.today() + timedelta(days=10),
            )
            promo.cars.set(random.sample(cars, k=random.randint(1, len(cars))))

        dealerships = []
        for i in range(1, 4):
            d = Dealership.objects.create(
                name=f"Dealership {i}",
                country="US",
                city=f"City {i}",
                balance=Decimal(random.randint(100000, 200000)),
            )
            dealerships.append(d)

        for dealership in dealerships:
            preferred = random.sample(cars, k=3)
            for car in preferred:
                PreferredModel.objects.create(
                    dealership=dealership, car=car, reason="Popular model"
                )

                offer_for_car: SupplierOffer | None = (
                    SupplierOffer.objects.filter(car=car).order_by("?").first()
                )

                if offer_for_car is None:
                    continue

                Inventory.objects.create(
                    dealership=dealership,
                    car=car,
                    quantity=random.randint(1, 10),
                    price=offer_for_car.price,
                )

        for buyer in buyers:
            for _ in range(2):
                car = random.choice(cars)
                dealership = random.choice(dealerships)
                Offer.objects.create(
                    buyer=buyer,
                    car=car,
                    dealership=dealership,
                    max_price=Decimal(random.randint(20000, 100000)),
                )

        logger.info("Test data created!")
