from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import  serializers
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

    level_id = serializers.PrimaryKeyRelatedField(
        queryset=Level.objects.all(), source='level', write_only=True, required=False, allow_null=True
    )
    form_id = serializers.PrimaryKeyRelatedField(
        queryset=Form.objects.all(), source='form', write_only=True, required=False, allow_null=True
    )
    topping_id = serializers.PrimaryKeyRelatedField(
        queryset=Topping.objects.all(), source='topping', write_only=True, required=False, allow_null=True
    )
    berry_id = serializers.PrimaryKeyRelatedField(
        queryset=Berry.objects.all(), source='berry', write_only=True, required=False, allow_null=True
    )
    decor_id = serializers.PrimaryKeyRelatedField(
        queryset=Decor.objects.all(), source='decor', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Cake
        fields = [
            'id', 'name', 'is_template', 'image', 'comment', 'words',
            'level', 'form', 'topping', 'berry', 'decor',
            'level_id', 'form_id', 'topping_id', 'berry_id', 'decor_id'
        ]

class PromoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promo
        fields = ['id', 'code', 'discount']


class OrderSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    cake = CakeSerializer()
    delivery_date = serializers.DateField()
    delivery_time = serializers.TimeField()
    promo = serializers.CharField(write_only=True, required=False, allow_null=True)

    def validate_promo(self, value):
        if value:
            value = value.strip()
            try:
                promo = Promo.objects.get(code=value, is_active=True)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Не верный промокод")
            if not promo.is_active:
                raise serializers.ValidationError("Не действительный промокод")
        return value

    @transaction.atomic
    def create(self, validated_data):
        sid = transaction.savepoint()
        user = self.context['request'].user
        cake_data = validated_data.pop('cake')
        promo_code = validated_data.pop('promo', None)
        cake_serializer = CakeSerializer(data=cake_data)
        cake = None
        if cake_serializer.is_valid(raise_exception=True):
            cake = cake_serializer.save()
        promo = None
        if promo_code:
            promo = Promo.objects.get(code=promo_code, is_active=True)

        try:
            order = Order.objects.create(
                cake=cake,
                promo=promo,
                **validated_data
            )
            order.total_price = order.calculate_total()
            order.save()
            return order
        except Exception as e:
            transaction.rollback(sid)
            raise serializers.ValidationError(f"Ошибка при создании заказа: {str(e)}")

    class Meta:
        model = Order
        fields = ['name','phone','email','address','promo']
