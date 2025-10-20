from django.urls import include, path
from rest_framework.routers import DefaultRouter

from suppliers.views import (
    SupplierOfferViewSet,
    SupplierPromotionViewSet,
    SupplierSaleHistoryViewSet,
    SupplierViewSet,
)

router = DefaultRouter()
router.register("suppliers", SupplierViewSet)
router.register("supplier-offers", SupplierOfferViewSet)
router.register("supplier-promotions", SupplierPromotionViewSet)
router.register("supplier-sales", SupplierSaleHistoryViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
