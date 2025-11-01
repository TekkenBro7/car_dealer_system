from django.urls import include, path
from rest_framework.routers import DefaultRouter

from dealerships.views import (
    DealershipPromotionViewSet,
    DealershipReportViewSet,
    DealershipSaleHistoryViewSet,
    DealershipViewSet,
    InventoryViewSet,
    PreferredModelViewSet,
)

router = DefaultRouter()
router.register("dealerships", DealershipViewSet)
router.register("dealership-inventories", InventoryViewSet)
router.register("dealership-preffers", PreferredModelViewSet)
router.register("dealership-promotions", DealershipPromotionViewSet)
router.register("dealership-sales", DealershipSaleHistoryViewSet)
router.register(
    "dealership-reports", DealershipReportViewSet, basename="dealership-report"
)


urlpatterns = [
    path("", include(router.urls)),
]
