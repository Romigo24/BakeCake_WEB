# serializers.py
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from webapp.models import Order, Cake, Level, Form, Topping, Berry, Decor, Promo


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ['id', 'name', 'price']


class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = ['id', 'name', 'price']


class ToppingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topping
        fields = ['id', 'name', 'price']


class BerrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Berry
        fields = ['id', 'name', 'price']


class DecorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Decor
        fields = ['id', 'name', 'price']


class CakeSerializer(serializers.ModelSerializer):
    level = LevelSerializer(read_only=True)
    form = FormSerializer(read_only=True)
    topping = ToppingSerializer(read_only=True)
    berry = BerrySerializer(read_only=True)
    decor = DecorSerializer(read_only=True)

    level_id = serializers.IntegerField(write_only=True)
    form_id = serializers.IntegerField(write_only=True)
    topping_id = serializers.IntegerField(write_only=True)
    berry_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    decor_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Cake
        fields = [
            'id', 'comment', 'words',
            'level', 'form', 'topping', 'berry', 'decor',
            'level_id', 'form_id', 'topping_id', 'berry_id', 'decor_id'
        ]

    def create(self, validated_data):
        return Cake.objects.create(**validated_data)


class OrderSerializer(serializers.ModelSerializer):
    cake = CakeSerializer()
    promo_code = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Order
        fields = [
            'id', 'name', 'phone', 'email', 'address', 
            'delivery_date', 'delivery_time', 'comments',
            'cake', 'promo_code'
        ]

    def validate(self, data):
        promo_code = data.get('promo_code', '').strip()
        if promo_code:
            try:
                promo = Promo.objects.get(code=promo_code, is_active=True)
                data['promo'] = promo
            except Promo.DoesNotExist:
                raise serializers.ValidationError({"promo_code": "Неверный промокод"})
        return data

    @transaction.atomic
    def create(self, validated_data):
        cake_data = validated_data.pop('cake')
        promo = validated_data.pop('promo', None)

        cake_serializer = CakeSerializer(data=cake_data)
        cake_serializer.is_valid(raise_exception=True)
        cake = cake_serializer.save()

        order = Order.objects.create(
            cake=cake,
            promo=promo,
            **validated_data
        )

        order.total_price = order.calculate_total()
        order.save()

        return order