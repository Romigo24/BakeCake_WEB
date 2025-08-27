from django.urls import path
from .views import catalog_options, price_quote, orders_create

urlpatterns = [
    path("catalog/options/", catalog_options, name="catalog_options"),
    path("price/quote/", price_quote, name="price_quote"),
    path("orders/create/", orders_create, name="orders_create"),
]
