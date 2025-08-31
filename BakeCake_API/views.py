from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone
from .payment_service import create_payment, check_payment_status
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from BakeCake_API.serializers import OrderSerializer, LevelSerializer, FormSerializer, ToppingSerializer, \
    BerrySerializer, DecorSerializer
from webapp.models import Order, Promo, Level, Form, Topping, Berry, Decor



def create_payment_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    return_url = request.build_absolute_uri(f'/order/{order_id}/payment/success/')

    payment = create_payment(order, return_url)

    order.yookassa_payment_id = payment.id
    order.payment_status = 'pending'
    order.save()

    return redirect(payment.confirmation.confirmation_url)


def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.yookassa_payment_id:
        payment_status = check_payment_status(order.yookassa_payment_id)

        if payment_status == 'succeeded':
            order.payment_status = 'succeeded'
            order.payment_date = timezone.now()
            order.save()

    return render(request, 'index.html', {'order': order})


@csrf_exempt
def yookassa_webhook(request):
    if request.method == 'POST':
        import json
        notification = json.loads(request.body)

        payment_id = notification['object']['id']
        payment_status = notification['object']['status']

        order = Order.objects.get(yookassa_payment_id=payment_id)

        if payment_status == 'succeeded':
            order.payment_status = 'succeeded'
            order.payment_date = timezone.now()
        elif payment_status == 'canceled':
            order.payment_status = 'canceled'

        order.save()

        return HttpResponse(status=200)

    return HttpResponse(status=400)


# заглушка для каталога опций
# views.py
class OptionsView(APIView):
    def get(self, request):
        levels = LevelSerializer(Level.objects.all(), many=True).data
        forms = FormSerializer(Form.objects.all(), many=True).data
        toppings = ToppingSerializer(Topping.objects.all(), many=True).data
        berries = BerrySerializer(Berry.objects.all(), many=True).data
        decors = DecorSerializer(Decor.objects.all(), many=True).data

        return Response({
            'levels': levels,
            'forms': forms,
            'toppings': toppings,
            'berries': berries,
            'decors': decors
        })


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
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def validate_promo(self, request):
        promo_code = request.data.get('promo', '').strip()

        try:
            promo = Promo.objects.get(code=promo_code, is_active=True)
            return Response({
                "valid": True,
                "discount": float(promo.discount)
            })
        except Promo.DoesNotExist:
            return Response({
                "valid": False,
                "error": "Недействительный промокод"
            }, status=400)

    def create(self, request, *args, **kwargs):
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
