from rest_framework import serializers
from datetime import datetime
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
        
        try:
            attrs["_date"] = (
                datetime.strptime(date_str, DATE_FORMAT).date()
                if date_str else None
            )
        except ValueError:
            raise serializers.ValidationError({"DATE": "Ожидается формат YYYY-MM-DD"})
        
        try:
            attrs["_time"] = (
                datetime.strptime(time_str, "%H:%M").time()
                if time_str else None
            )
        except ValueError:
            raise serializers.ValidationError({"TIME": "Ожидается формат HH:MM"})

        client_total = attrs.get("CLIENT_TOTAL")
        if client_total is not None and client_total != attrs["_total"]:
            attrs["_price_mismatch"] = True
            
        return attrs

    def create(self, validated):
        details = {
            "Levels":  validated.get("LEVELS","0"),
            "Form":    validated.get("FORM","0"),
            "Topping": validated.get("TOPPING","0"),
            "Berries": validated.get("BERRIES","0"),
            "Decor":   validated.get("DECOR","0"),
            "Words":   (validated.get("WORDS") or "").strip(),
            "Comments":(validated.get("COMMENTS") or "").strip(),
            "Name":    (validated.get("NAME") or "").strip(),
            "Phone":   (validated.get("PHONE") or "").strip(),
            "Email":   (validated.get("EMAIL") or "").strip(),
        }
        
        return Order.objects.create(
            customer=validated.get("NAME") or None,
            customer_chat_id=None,
            order_details=details,
            order_price=validated["_total"],
            delivery_address=(validated.get("ADDRESS") or "").strip(),
            delivery_date=validated["_date"],
            delivery_time=validated["_time"],
            comments=(validated.get("DELIVCOMMENTS") or "").strip(),
            order_type=Order.Assembly,
        )
