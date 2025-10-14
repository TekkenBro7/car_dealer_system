from django.contrib import admin

from cars.models import BodyType, Car, CarBrand

admin.site.register(CarBrand)
admin.site.register(BodyType)
admin.site.register(Car)
