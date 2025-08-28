from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Promo(models.Model):
    code = models.CharField(verbose_name='Промокод',max_length=50, unique=True)
    discount_percent = models.PositiveIntegerField(
        verbose_name='Процент скидки',
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=5
    )
    max_usage_count = models.PositiveIntegerField(
        verbose_name='Количество использований',
        default=1
    )
    current_usage_count = models.PositiveIntegerField(
        verbose_name='Текущее количество использований',
        default=0
    )
    is_active = models.BooleanField(verbose_name='Активен',default=True)

    def __str__(self):
        return f"{self.code} {self.discount_percent}%"

    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'



class Cake(models.Model):
    name = models.CharField(verbose_name='Название торта', max_length=50)
    image = models.ImageField(verbose_name='Изображение торта')
    description = models.CharField(verbose_name='Описание', max_length=100)
    price = models.PositiveIntegerField(verbose_name='Цена')
    weight = models.DecimalField(verbose_name='Вес торта', max_digits=4, decimal_places=2)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Торт'
        verbose_name_plural = 'Торты'

class Customer(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='Внешний ID покупателя',
        unique=True
    )
    tg_username = models.CharField('Имя покупателя в Telegram', max_length=50, blank=True)
    first_name = models.CharField('Имя', max_length=5, blank=True, null=True)
    last_name = models.CharField('Фамилия', max_length=256, blank=True, null=True)
    phone_number = PhoneNumberField()
    GDPR_status = models.BooleanField(null=True, default=False)
    home_address = models.CharField('Домашний адрес', max_length=50, blank=True, null=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name} (ID: {self.external_id})'
    
    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'


class Product(models.Model):
    product_name = models.CharField(max_length=256)

    def __str__(self):
        return f'{self.product_name}'
    
    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'


class Product_properties(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    property_name = models.CharField(max_length=256)

    def __str__(self):
        return f'{self.property_name}'
    
    class Meta:
        verbose_name = 'Свойства продукта'
        verbose_name_plural = 'Свойства продуктов'


class Product_parameters(models.Model):
    product_property = models.ForeignKey(Product_properties, verbose_name='Свойства продукта', on_delete=models.CASCADE)
    parameter_name = models.CharField(verbose_name='Название параметра', max_length=256)
    parameter_price = models.PositiveIntegerField(verbose_name='Цена')

    class Meta:
        verbose_name = 'Параметры продукта'
        verbose_name_plural = 'Парметры продуктов'


class Order(models.Model):
    customer = models.CharField(verbose_name='Имя покупателя', blank=True, null=True, max_length=256)
    customer_chat_id = models.CharField(verbose_name='Chat ID покупателя', null=True, blank=True, max_length=256)
    order_details = models.JSONField(verbose_name='Детали заказа', default='Пока ничего нет')
    order_price = models.PositiveIntegerField(verbose_name='Цена заказа')
    Processing = 'Заявка обрабатывается'
    Cooking = 'Готовим ваш торт'
    Transport = 'Продукт в пути'
    Delivered = 'Продукт у вас'
    order_statuses = [
        (Processing, 'Заявка обрабатывается'),
        (Cooking, 'Готовим ваш торт'),
        (Transport, 'Продукт в пути'),
        (Delivered, 'Продукт у вас'),
    ]
    order_status = models.CharField(verbose_name='Статус заказа',
                                    max_length=256,
                                    choices=order_statuses,
                                    default=Processing,)
    comments = models.CharField(verbose_name='Комментарии', null=True, blank=True, max_length=256)
    delivery_address = models.CharField(verbose_name='Адрес доставки', max_length=256, default=' ')
    delivery_date = models.DateField(verbose_name='Дата доставки', blank=True, null=True)
    delivery_time = models.TimeField(verbose_name='Время доставки', blank=True, null=True)
    cake_name = models.ForeignKey(Cake,
                                  verbose_name='Название торта',
                                  related_name='orders',
                                  blank=True,
                                  null=True,
                                  on_delete=models.CASCADE)
    Assembly = 'Собрать свой торт'
    Ordering = 'Закзать торт'
    order_types = [
        (Assembly, 'Собрать свой торт'),
        (Ordering, 'Заказать торт')
    ]
    order_type = models.CharField(verbose_name='Тип заказа', max_length=17, choices=order_types, default=Ordering,)

    promo = models.ForeignKey(Promo,on_delete=models.SET_NULL,null=True, blank=True)

    def __str__(self):
        date_value =  self.delivery_time.isoformat(timespec='minutes') if self.delivery_time else 'Дата не установлена'
        return f"{date_value}"
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

