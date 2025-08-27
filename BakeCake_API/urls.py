from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .views import catalog_options, price_quote, orders_create


@api_view(["GET"])
def api_root(_request):
    return Response({
        "catalog_options": "/api/v1/catalog/options/",
        "price_quote": "/api/v1/price/quote/",
        "orders_create": "/api/v1/orders/create/",
    })


urlpatterns = [
    path("", api_root, name="api_root"),
    path("catalog/options/", catalog_options, name="catalog_options"),
    path("price/quote/", price_quote, name="price_quote"),
    path("orders/create/", orders_create, name="orders_create"),
]
