from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta, datetime

from .serializers import QuoteSerializer, OrderCreateSerializer
from webapp.models import Order
from .pricing import OPTIONS


@api_view(["GET"])
def catalog_options(_request):
    response_data = {
        "levels": {
            "values": OPTIONS["Levels"]["values"],
            "prices": OPTIONS["Levels"]["prices"]
        },
        "forms": {
            "values": OPTIONS["Forms"]["values"],
            "prices": OPTIONS["Forms"]["prices"]
        },
        "toppings": {
            "values": OPTIONS["Toppings"]["values"],
            "prices": OPTIONS["Toppings"]["prices"]
        },
        "berries": {
            "values": OPTIONS["Berries"]["values"],
            "prices": OPTIONS["Berries"]["prices"]
        },
        "decors": {
            "values": OPTIONS["Decors"]["values"],
            "prices": OPTIONS["Decors"]["prices"]
        },
        "words_price": OPTIONS["Words"]
    }
    return Response(response_data)


@api_view(["POST"])
def price_quote(request):
    serializer = QuoteSerializer(data=request.data)
    
    if serializer.is_valid():
        total_price = serializer.validated_data["_total"]
        
        date_str = request.data.get("DATE", "")
        time_str = request.data.get("TIME", "")
        
        urgent_surcharge = 0
        is_urgent = False
        
        if date_str and time_str:
            try:
                from datetime import datetime
                delivery_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                delivery_time = datetime.strptime(time_str, "%H:%M").time()
                
                delivery_datetime = timezone.make_aware(
                    datetime.combine(delivery_date, delivery_time)
                )
                current_datetime = timezone.now()
                
                if (delivery_datetime - current_datetime) <= timedelta(hours=24):
                    is_urgent = True
                    urgent_surcharge = int(total_price * 0.2)
                    total_price += urgent_surcharge
                    
            except (ValueError, TypeError):
                pass
        
        response_data = {
            "total": total_price,
            "base_price": serializer.validated_data["_total"],
            "is_urgent": is_urgent,
            "urgent_surcharge": urgent_surcharge if is_urgent else 0,
            "details": {
                "levels": request.data.get("LEVELS", "0"),
                "form": request.data.get("FORM", "0"),
                "topping": request.data.get("TOPPING", "0"),
                "berries": request.data.get("BERRIES", "0"),
                "decor": request.data.get("DECOR", "0"),
                "words": request.data.get("WORDS", "")
            }
        }
        return Response(response_data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def orders_create(request):
    serializer = OrderCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            order = serializer.save()
            
            response_data = {
                "order_id": order.id,
                "total": order.order_price,
                "is_urgent": order.is_urgent,
                "urgent_surcharge": order.urgent_surcharge,
                "delivery_date": order.delivery_date.isoformat() if order.delivery_date else None,
                "delivery_time": order.delivery_time.isoformat() if order.delivery_time else None,
                "status": order.order_status
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            error_data = {
                "error": "Ошибка при создании заказа",
                "details": str(e)
            }
            return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    if serializer.validated_data.get("_price_mismatch", False):
        error_data = {
            "error": "Цена изменилась",
            "server_total": serializer.validated_data.get("_total", 0),
            "client_total": request.data.get("CLIENT_TOTAL")
        }
        return Response(error_data, status=status.HTTP_409_CONFLICT)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def order_status(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        response_data = {
            "order_id": order.id,
            "status": order.order_status,
            "total": order.order_price,
            "is_urgent": order.is_urgent,
            "urgent_surcharge": order.urgent_surcharge,
            "delivery_date": order.delivery_date.isoformat() if order.delivery_date else None,
            "delivery_time": order.delivery_time.isoformat() if order.delivery_time else None,
            "customer_name": order.customer,
            "customer_phone": order.phone,
            "delivery_address": order.delivery_address
        }
        return Response(response_data)
        
    except Order.DoesNotExist:
        return Response(
            {"error": "Заказ не найден"}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
def order_history(request):
    phone = request.GET.get('phone')
    email = request.GET.get('email')
    
    orders = Order.objects.all().order_by('-created_at')[:10]  # Последние 10 заказов
    
    if phone:
        orders = orders.filter(phone__icontains=phone)
    if email:
        orders = orders.filter(email__icontains=email)
    
    orders_data = []
    for order in orders:
        orders_data.append({
            "order_id": order.id,
            "date": order.created_at.isoformat() if order.created_at else None,
            "status": order.order_status,
            "total": order.order_price,
            "is_urgent": order.is_urgent,
            "items": [
                f"{OPTIONS['Levels']['values'][int(order.levels)] if order.levels else 'Не указано'} уровней",
                f"Форма: {OPTIONS['Forms']['values'][int(order.form)] if order.form else 'Не указано'}",
                f"Топпинг: {OPTIONS['Toppings']['values'][int(order.topping)] if order.topping else 'Не указано'}",
                f"Ягоды: {OPTIONS['Berries']['values'][int(order.berries)] if order.berries else 'Нет'}",
                f"Декор: {OPTIONS['Decors']['values'][int(order.decor)] if order.decor else 'Нет'}",
                f"Надпись: {order.words if order.words else 'Нет'}"
            ]
        })
    
    return Response({"orders": orders_data})


@api_view(["POST"])
def validate_delivery_time(request):
    date_str = request.data.get("date", "")
    time_str = request.data.get("time", "")
    
    if not date_str or not time_str:
        return Response(
            {"error": "Требуются дата и время"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        delivery_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        delivery_time = datetime.strptime(time_str, "%H:%M").time()
        
        delivery_datetime = timezone.make_aware(
            datetime.combine(delivery_date, delivery_time)
        )
        current_datetime = timezone.now()
        
        min_delivery_time = current_datetime + timedelta(hours=5)
        
        if delivery_datetime < current_datetime:
            return Response({
                "valid": False,
                "reason": "Указанные дата и время уже прошли"
            })
        
        if delivery_datetime < min_delivery_time:
            min_time_str = min_delivery_time.strftime("%d.%m.%Y %H:%M")
            return Response({
                "valid": False,
                "reason": f"Минимальное время заказа - через 5 часов. Ближайшее доступное время: {min_time_str}"
            })
        
        is_urgent = (delivery_datetime - current_datetime) <= timedelta(hours=24)
        
        is_within_hours = 10 <= delivery_time.hour < 23
        
        response_data = {
            "valid": is_within_hours and (delivery_datetime >= min_delivery_time),
            "is_urgent": is_urgent,
            "delivery_datetime": delivery_datetime.isoformat(),
            "min_delivery_time": min_delivery_time.isoformat()
        }
        
        if not is_within_hours:
            response_data["reason"] = "Доставка возможна только с 10:00 до 23:00"
        elif delivery_datetime < min_delivery_time:
            response_data["reason"] = f"Минимальное время заказа - через 5 часов"
        
        return Response(response_data)
        
    except ValueError:
        return Response(
            {"error": "Неверный формат даты или времени"},
            status=status.HTTP_400_BAD_REQUEST
        )
