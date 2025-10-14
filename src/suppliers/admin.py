from django.contrib import admin

from suppliers.models import (
    Supplier,
    SupplierOffer,
    SupplierPromotion,
    SupplierSaleHistory,
)

admin.site.register(Supplier)
admin.site.register(SupplierOffer)
admin.site.register(SupplierPromotion)
admin.site.register(SupplierSaleHistory)
