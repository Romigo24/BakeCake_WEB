from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OptionsView, OrdersViewSet, price_quote, OrderCakeViewSet


router = DefaultRouter()
# router.register("catalog/options", OptionsView.as_view(), basename="options")
router.register("orders", OrdersViewSet, basename="orders")

router.register('ordercake', OrderCakeViewSet, basename="ordercake")

urlpatterns = [
    path("", include(router.urls)),
    path("price/quote", price_quote),
    path("options/", OptionsView.as_view()),
]
