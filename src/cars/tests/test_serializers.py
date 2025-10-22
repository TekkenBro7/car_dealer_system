from typing import Any

from django.test import TestCase

from cars.models import BodyType, Car, CarBrand
from cars.serializers import (
    BodyTypeSerializer,
    CarBrandSerializer,
    CarDetailSerializer,
    CarListSerializer,
)


class CarBrandSerializerTest(TestCase):
    def setUp(self) -> None:
        self.valid_data = {
            "name": "Toyota",
            "country": "JP",
        }

    def test_create_car_brand(self) -> None:
        serializer = CarBrandSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        brand = serializer.save()
        self.assertEqual(brand.name, "Toyota")
        self.assertEqual(brand.country.code, "JP")

    def test_unique_name_validation(self) -> None:
        CarBrand.objects.create(**self.valid_data)
        serializer = CarBrandSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_update_car_brand(self) -> None:
        brand = CarBrand.objects.create(name="Toyota", country="JP")

        update_data = {"name": "Toyota Motors", "country": "US"}

        serializer = CarBrandSerializer(instance=brand, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())

        updated_brand = serializer.save()
        self.assertEqual(updated_brand.name, "Toyota Motors")
        self.assertEqual(updated_brand.country, "US")

    def test_serializer_fields(self) -> None:
        brand = CarBrand.objects.create(name="Toyota", country="JP")
        serializer = CarBrandSerializer(instance=brand)

        expected_fields = {
            "id",
            "name",
            "country",
            "created_at",
            "updated_at",
            "is_active",
        }

        self.assertEqual(serializer.data.keys(), expected_fields)


class TestBodyTypeSerializer(TestCase):
    def setUp(self) -> None:
        self.valid_data = {"name": "Sedan"}

    def test_valid_serializer_data(self) -> None:
        serializer = BodyTypeSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_required_fields(self) -> None:
        invalid_data: dict[str, Any] = {}

        serializer = BodyTypeSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_unique_name_validation(self) -> None:
        BodyType.objects.create(name="Sedan")

        serializer = BodyTypeSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_create_body_type(self) -> None:
        serializer = BodyTypeSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

        body_type = serializer.save()

        self.assertIsInstance(body_type, BodyType)
        self.assertEqual(body_type.name, "Sedan")
        self.assertTrue(body_type.is_active)

    def test_serializer_fields(self) -> None:
        body_type = BodyType.objects.create(name="Sedan")
        serializer = BodyTypeSerializer(instance=body_type)

        expected_fields = {
            "id",
            "name",
            "created_at",
            "updated_at",
            "is_active",
        }

        self.assertEqual(serializer.data.keys(), expected_fields)


class TestCarListSerializer(TestCase):
    def setUp(self) -> None:
        self.brand = CarBrand.objects.create(name="Toyota", country="JP")
        self.body_type = BodyType.objects.create(name="Sedan")

        self.valid_data = {
            "model_name": "Camry",
            "brand": self.brand.id,
            "body_type": self.body_type.id,
        }

    def test_valid_serializer_data(self) -> None:
        serializer = CarListSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.data["is_active"], True)

    def test_required_fields(self) -> None:
        required_fields = ["model_name", "brand"]

        for field in required_fields:
            invalid_data = self.valid_data.copy()
            del invalid_data[field]

            serializer = CarListSerializer(data=invalid_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn(field, serializer.errors)

    def test_body_type_optional(self) -> None:
        data_without_body_type = {"model_name": "Camry", "brand": self.brand.id}

        serializer = CarListSerializer(data=data_without_body_type)
        self.assertTrue(serializer.is_valid())

    def test_create_car(self) -> None:
        serializer = CarListSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

        car = serializer.save()

        self.assertIsInstance(car, Car)
        self.assertEqual(car.model_name, "Camry")
        self.assertEqual(car.brand, self.brand)
        self.assertEqual(car.body_type, self.body_type)
        self.assertTrue(car.is_active)

    def test_serializer_fields(self) -> None:
        car = Car.objects.create(
            brand=self.brand, model_name="Camry", body_type=self.body_type
        )
        serializer = CarListSerializer(instance=car)

        expected_fields = {
            "id",
            "model_name",
            "brand",
            "body_type",
            "created_at",
            "updated_at",
            "is_active",
        }

        self.assertEqual(serializer.data.keys(), expected_fields)


class TestCarDetailSerializer(TestCase):
    def setUp(self) -> None:
        self.brand = CarBrand.objects.create(name="Toyota", country="JP")
        self.body_type = BodyType.objects.create(name="Sedan")
        self.car = Car.objects.create(
            brand=self.brand, model_name="Camry", body_type=self.body_type
        )

    def test_serializer_fields(self) -> None:
        serializer = CarDetailSerializer(instance=self.car)

        expected_fields = {
            "id",
            "brand",
            "body_type",
            "model_name",
            "created_at",
            "updated_at",
            "is_active",
        }

        self.assertEqual(serializer.data.keys(), expected_fields)

    def test_nested_serializers(self) -> None:
        serializer = CarDetailSerializer(instance=self.car)

        self.assertIsInstance(serializer.data["brand"], dict)
        self.assertIsInstance(serializer.data["body_type"], dict)

        self.assertEqual(serializer.data["brand"]["name"], "Toyota")
        self.assertEqual(serializer.data["body_type"]["name"], "Sedan")
