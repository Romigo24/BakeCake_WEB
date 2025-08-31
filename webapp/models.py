from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Level(models.Model):
    name = models.CharField(max_length=20, verbose_name="Название уровня")
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name

class Form(models.Model):
    name = models.CharField(max_length=20, verbose_name="Название формы")
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name

class Topping(models.Model):
    name = models.CharField(max_length=20, verbose_name="Название топпинга")
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name

class Berry(models.Model):
    name = models.CharField(max_length=20, verbose_name="Название ягоды")
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name

class Decor(models.Model):
    name = models.CharField(max_length=20, verbose_name="Название декора")
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name

class Cake(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название торта")
    is_template = models.BooleanField(default=False, verbose_name="Заготовка")
    image = models.ImageField(upload_to='cakes/', blank=True, null=True, verbose_name="Изображение")
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Уровень")
    form = models.ForeignKey(Form, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Форма")
    topping = models.ForeignKey(Topping, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Топпинг")
    berry = models.ForeignKey(Berry, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Ягода")
    decor = models.ForeignKey(Decor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Декор")
    words = models.CharField(max_length=100, blank=True, verbose_name="Надпись")
    comment = models.TextField(blank=True, verbose_name="Комментарий")

    def calculate_price(self):
        price = 0
        if self.level:
            price += self.level.price
        if self.form:
            price += self.form.price
        if self.topping:
            price += self.topping.price
        if self.berry:
            price += self.berry.price
        if self.decor:
            price += self.decor.price
        if self.words:
            price += 500  # Стоимость надписи
        return price

    def __str__(self):
        return f'Заказ {self.id}'

class Promo(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Код промокода")
    discount = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Скидка в %")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    def __str__(self):
        return self.code

class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('completed', 'Выполнен'),
        ('cancelled', 'Отменен'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Пользователь")
    cake = models.ForeignKey(Cake, on_delete=models.CASCADE, verbose_name="Торт")
    name = models.CharField(max_length=100, verbose_name="Имя")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    address = models.TextField(verbose_name="Адрес доставки")
    delivery_date = models.DateField(verbose_name="Дата доставки")
    delivery_time = models.TimeField(verbose_name="Время доставки")
    promo = models.ForeignKey(Promo, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Промокод")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Общая стоимость", null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    comments = models.TextField(blank=True, null=True)

    def calculate_total(self):
        total = self.cake.calculate_price()
        if self.promo:
            total = total * (1 - self.promo.discount / 100)
        return total


    def __str__(self):
        return f"Заказ #{self.id} от {self.created_at}"