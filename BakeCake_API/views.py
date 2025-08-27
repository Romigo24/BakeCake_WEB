from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny


# заглушка для каталога опций
class OptionsViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        return Response({"options": []})


# заглушка для заказов
class OrdersViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        return Response({"orders": []})

    def create(self, request):
        return Response({"status": "created"})


# заглушка для price/quote
@api_view(["POST"])
def price_quote(request):
    return Response({"subtotal": 0, "total": 0})
