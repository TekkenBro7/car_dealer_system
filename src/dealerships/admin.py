from django.contrib import admin

from dealerships.models import (
    Dealership,
    DealershipPromotion,
    DealershipSaleHistory,
    Inventory,
    PreferredModel,
)

admin.site.register(Dealership)
admin.site.register(Inventory)
admin.site.register(PreferredModel)
admin.site.register(DealershipPromotion)
admin.site.register(DealershipSaleHistory)
