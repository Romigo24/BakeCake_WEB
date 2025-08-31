from django.contrib import admin
from .models import Level, Form, Berry, Topping, Decor, Promo, Order, Cake


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    pass

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    pass

@admin.register(Berry)
class BerryAdmin(admin.ModelAdmin):
    pass

@admin.register(Topping)
class ToppingAdmin(admin.ModelAdmin):
    pass

@admin.register(Decor)
class DecorAdmin(admin.ModelAdmin):
    pass

@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    pass

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass

@admin.register(Cake)
class CakeAdmin(admin.ModelAdmin):
    pass

# Register your models here.
