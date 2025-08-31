# serializers.py
from rest_framework import serializers
from datetime import datetime, timedelta
from django.utils import timezone
from webapp.models import Order
from .pricing import calc_total


DATE_FORMAT = "%Y-%m-%d"


class QuoteSerializer(serializers.Serializer):
    LEVELS = serializers.CharField(required=False, allow_blank=True, default="0")
    FORM = serializers.CharField(required=False, allow_blank=True, default="0")
    TOPPING = serializers.CharField(required=False, allow_blank=True, default="0")
    BERRIES = serializers.CharField(required=False, allow_blank=True, default="0")
    DECOR = serializers.CharField(required=False, allow_blank=True, default="0")
    WORDS = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, attrs):
        details = {
            "Levels": attrs.get("LEVELS", "0"),
            "Form": attrs.get("FORM", "0"),
            "Topping": attrs.get("TOPPING", "0"),
            "Berries": attrs.get("BERRIES", "0"),
            "Decor": attrs.get("DECOR", "0"),
            "Words": (attrs.get("WORDS") or "").strip(),
        }
        attrs["_total"] = calc_total(details)
        return attrs


class OrderCreateSerializer(QuoteSerializer):
    COMMENTS = serializers.CharField(required=False, allow_blank=True, default="")
    NAME = serializers.CharField(required=False, allow_blank=True, default="")
    PHONE = serializers.CharField(required=False, allow_blank=True, default="")
    EMAIL = serializers.EmailField(required=False, allow_blank=True, default="")
    ADDRESS = serializers.CharField(required=False, allow_blank=True, default="")
    DATE = serializers.CharField(required=False, allow_blank=True, default="")
    TIME = serializers.CharField(required=False, allow_blank=True, default="")
    DELIVCOMMENTS = serializers.CharField(required=False, allow_blank=True, default="")
    CLIENT_TOTAL = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)

        date_str = attrs.get("DATE") or ""
        time_str = attrs.get("TIME") or ""
        
        attrs["_date"] = None
        if date_str:
            try:
                attrs["_date"] = datetime.strptime(date_str, DATE_FORMAT).date()
            except ValueError:
                raise serializers.ValidationError({"DATE": "Ожидается формат YYYY-MM-DD"})
        
        attrs["_time"] = None
        if time_str:
            try:
                attrs["_time"] = datetime.strptime(time_str, "%H:%M").time()
            except ValueError:
                raise serializers.ValidationError({"TIME": "Ожидается формат HH:MM"})

        if attrs["_date"] and attrs["_date"] < timezone.now().date():
            raise serializers.ValidationError({"DATE": "Дата доставки не может быть в прошлом"})
        
        if attrs["_date"] and attrs["_time"]:
            delivery_datetime = timezone.make_aware(
                datetime.combine(attrs["_date"], attrs["_time"])
            )
            current_datetime = timezone.now()
            min_delivery_time = current_datetime + timedelta(hours=5)
            
            if delivery_datetime < min_delivery_time:
                min_time_str = min_delivery_time.strftime("%d.%m.%Y %H:%M")
                raise serializers.ValidationError({
                    "TIME": f"Минимальное время заказа - через 5 часов. Ближайшее доступное время: {min_time_str}"
                })
            
            if (attrs["_date"] == timezone.now().date() and 
                attrs["_time"] and 
                attrs["_time"] < timezone.now().time()):
                raise serializers.ValidationError({"TIME": "Время доставки не может быть в прошлом для сегодняшнего дня"})

        attrs["_is_urgent"] = False
        attrs["_urgent_surcharge"] = 0
        
        if attrs["_date"] and attrs["_time"]:
            try:
                delivery_datetime = timezone.make_aware(
                    datetime.combine(attrs["_date"], attrs["_time"])
                )
                current_datetime = timezone.now()
                
                time_difference = delivery_datetime - current_datetime
                if time_difference <= timedelta(hours=24):
                    attrs["_is_urgent"] = True
                    attrs["_urgent_surcharge"] = int(attrs["_total"] * 0.2)
                    attrs["_total"] += attrs["_urgent_surcharge"]
                    
            except (ValueError, TypeError) as e:
                print(f"Error calculating urgency: {e}")

        client_total = attrs.get("CLIENT_TOTAL")
        if client_total is not None and client_total != attrs["_total"]:
            attrs["_price_mismatch"] = True
            
        return attrs

    def create(self, validated_data):
        details = {
            "Levels": validated_data.get("LEVELS", "0"),
            "Form": validated_data.get("FORM", "0"),
            "Topping": validated_data.get("TOPPING", "0"),
            "Berries": validated_data.get("BERRIES", "0"),
            "Decor": validated_data.get("DECOR", "0"),
            "Words": (validated_data.get("WORDS") or "").strip(),
            "Comments": (validated_data.get("COMMENTS") or "").strip(),
            "Name": (validated_data.get("NAME") or "").strip(),
            "Phone": (validated_data.get("PHONE") or "").strip(),
            "Email": (validated_data.get("EMAIL") or "").strip(),
        }
        
        order_data = {
            'customer': validated_data.get("NAME") or None,
            'order_details': details,
            'order_price': validated_data["_total"],
            'delivery_address': (validated_data.get("ADDRESS") or "").strip(),
            'delivery_date': validated_data.get("_date"),
            'delivery_time': validated_data.get("_time"),
            'comments': (validated_data.get("DELIVCOMMENTS") or "").strip(),
            'order_type': 'Собрать свой торт',
            'phone': (validated_data.get("PHONE") or "").strip(),
            'email': (validated_data.get("EMAIL") or "").strip(),
            'levels': str(validated_data.get("LEVELS", "0")),
            'form': str(validated_data.get("FORM", "0")),
            'topping': str(validated_data.get("TOPPING", "0")),
            'berries': str(validated_data.get("BERRIES", "0")),
            'decor': str(validated_data.get("DECOR", "0")),
            'words': (validated_data.get("WORDS") or "").strip(),
            'order_comments': (validated_data.get("COMMENTS") or "").strip(),
            'is_urgent': validated_data.get("_is_urgent", False),
            'urgent_surcharge': validated_data.get("_urgent_surcharge", 0),
        }
        
        return Order.objects.create(**order_data)