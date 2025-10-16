from django.db import IntegrityError
from django.test import TestCase

from cars.models import BodyType, Car, CarBrand


class CarBrandModelTest(TestCase):
    def setUp(self) -> None:
        self.brand_data = {"name": "Toyota", "country": "Japan"}

    def test_car_brand_creation(self) -> None:
        brand = CarBrand.objects.create(**self.brand_data)

        self.assertEqual(brand.name, "Toyota")
        self.assertEqual(brand.country, "Japan")
        self.assertIsNotNone(brand.created_at)
        self.assertIsNotNone(brand.updated_at)

    def test_car_brand_string_representation(self) -> None:
        brand = CarBrand.objects.create(**self.brand_data)

        self.assertEqual(str(brand), "Toyota")

    def test_car_brand_unique_name(self) -> None:
        CarBrand.objects.create(**self.brand_data)

        with self.assertRaises(IntegrityError):
            CarBrand.objects.create(name="Toyota", country="USA")

    def test_car_brand_optional_country(self) -> None:
        brand_without_country = CarBrand.objects.create(name="Tesla")

        self.assertEqual(brand_without_country.name, "Tesla")
        self.assertIsNone(brand_without_country.country)


class BodyTypeModelTest(TestCase):
    def setUp(self) -> None:
        self.body_type_data = {"name": "Sedan"}

    def test_body_type_creation(self) -> None:
        body_type = BodyType.objects.create(**self.body_type_data)

        self.assertEqual(body_type.name, "Sedan")
        self.assertIsNotNone(body_type.created_at)
        self.assertIsNotNone(body_type.updated_at)

    def test_body_type_string_representation(self) -> None:
        body_type = BodyType.objects.create(**self.body_type_data)

        self.assertEqual(str(body_type), "Sedan")

    def test_body_type_unique_name(self) -> None:
        BodyType.objects.create(**self.body_type_data)

        with self.assertRaises(IntegrityError):
            BodyType.objects.create(name="Sedan")


class CarModelsTest(TestCase):
    def setUp(self) -> None:
        self.brand = CarBrand.objects.create(name="Toyota", country="Japan")
        self.body_type = BodyType.objects.create(name="Sedan")

    def test_car_creation(self) -> None:
        car = Car.objects.create(
            brand=self.brand, body_type=self.body_type, model_name="Camry"
        )
        self.assertEqual(car.brand, self.brand)
        self.assertEqual(car.body_type, self.body_type)
        self.assertEqual(car.model_name, "Camry")
        self.assertIsNotNone(car.pk)
        self.assertEqual(str(car), "Toyota Camry")

    def test_car_unique_together(self) -> None:
        Car.objects.create(
            brand=self.brand, body_type=self.body_type, model_name="Camry"
        )

        with self.assertRaises(IntegrityError):
            Car.objects.create(
                brand=self.brand, body_type=self.body_type, model_name="Camry"
            )

    def test_car_unique_together_different_brands(self) -> None:
        honda = CarBrand.objects.create(name="Honda", country="Japan")
        honda_camry = Car.objects.create(
            brand=honda, body_type=self.body_type, model_name="Camry"
        )

        Car.objects.create(
            brand=self.brand, body_type=self.body_type, model_name="Camry"
        )

        self.assertEqual(honda_camry.model_name, "Camry")
        self.assertEqual(honda_camry.brand.name, "Honda")

    def test_car_unique_together_different_models_same_brand(self) -> None:
        Car.objects.create(
            brand=self.brand, body_type=self.body_type, model_name="Camry"
        )
        corolla = Car.objects.create(
            brand=self.brand, body_type=self.body_type, model_name="Corolla"
        )

        self.assertEqual(corolla.model_name, "Corolla")
        self.assertEqual(corolla.brand, self.brand)
