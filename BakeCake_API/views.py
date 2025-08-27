from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)

from .pricing import OPTIONS
from .serializers import OrderCreateSerializer, QuoteSerializer


@extend_schema(
    tags=["v1"],
    operation_id="catalog_options",
    description="Возвращает варианты и цены для конструктора торта.",
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    "Пример",
                    value={
                        "levels": {
                            "values": ["не выбрано","1","2","3"], 
                            "prices":[0,400,750,1100]
                        },
                        "forms": {
                            "values": ["не выбрано","Круг","Квадрат","Прямоугольник"],
                            "prices":[0,600,400,1000]
                        },
                        "toppings": {
                            "values": ["не выбрано","Без","Белый соус","Карамельный","Кленовый","Черничный","Молочный шоколад","Клубничный"],
                            "prices":[0,0,200,180,200,300,350,200]
                        },
                        "berries": {
                            "values":["нет","Ежевика","Малина","Голубика","Клубника"],
                            "prices":[0,400,300,450,500]
                        },
                        "decors": {
                            "values":["нет","Фисташки","Безе","Фундук","Пекан","Маршмеллоу","Марципан"],
                            "prices":[0,300,400,350,300,200,280]
                        },
                        "words_price": 500
                    }
                )
            ]
        )
    }
)
@api_view(["GET"])
@permission_classes([AllowAny])
def catalog_options(_request):
    return Response(
        {
            "levels": OPTIONS["Levels"],
            "forms": OPTIONS["Forms"],
            "toppings": OPTIONS["Toppings"],
            "berries": OPTIONS["Berries"],
            "decors": OPTIONS["Decors"],
            "words_price": OPTIONS["Words"],
        }
    )


@extend_schema(
    tags=["v1"],
    operation_id="price_quote",
    description="Считает цену на сервере по переданным опциям.",
    request=QuoteSerializer,
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            examples=[OpenApiExample("OK", value={"total": 2930})]
        ),
        400: OpenApiResponse(description="Ошибка валидации")
    }
)
@api_view(["POST"])
@permission_classes([AllowAny])
def price_quote(request):
    serializer = QuoteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response({"total": serializer.validated_data["_total"]})


@extend_schema(
    tags=["v1"],
    operation_id="orders_create",
    description=(
        "Создаёт заказ. Клиент может прислать локально посчитанный `CLIENT_TOTAL` - "
        "сервер проверит совпадение и вернёт 409 при расхождении."
    ),
    request=OrderCreateSerializer,
    responses={
        201: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample("Создано", value={"ok": True, "order_id": 12, "total": 2930})
            ]
        ),
        409: OpenApiResponse(
            description="Несовпадение цены",
            examples=[
                OpenApiExample("Mismatch", value={"ok": False, "reason": "price_mismatch", "server_total": 3000})
            ]
        ),
        400: OpenApiResponse(description="Ошибка валидации")
    }
)
@api_view(["POST"])
@permission_classes([AllowAny])
def orders_create(request):
    serializer = OrderCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if serializer.validated_data.get("_price_mismatch"):
        return Response(
            {
                "ok": False, 
                "reason": "price_mismatch", 
                "server_total": serializer.validated_data["_total"],
            },
            status=status.HTTP_409_CONFLICT
        )
        
    order = serializer.save()
    return Response(
        {"ok": True, "order_id": order.id, "total": order.order_price},
        status=status.HTTP_201_CREATED,
    )
