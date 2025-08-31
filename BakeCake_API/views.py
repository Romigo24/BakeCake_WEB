from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny

from BakeCake_API.serializers import OrderSerializer
from webapp.models import Order


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


class OrderCakeViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().select_related('cake', 'promo', 'user')
    serializer_class = OrderSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            user = self.request.user
            return self.queryset.filter(user=user)
        return Order.objects.none()

    def create(self, request, *args, **kwargs):
        test =  request.data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = serializer.save()
            return Response(
                {"id": order.id, "status": "created", "total_price": order.total_price},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )




