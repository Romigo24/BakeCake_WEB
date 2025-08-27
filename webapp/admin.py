from django.contrib import admin
from django.utils.html import format_html
from .models import Cake, Customer, Product, Product_properties, Product_parameters, Order

@admin.register(Cake)
class CakeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'weight', 'image_preview')
    list_filter = ('price',)
    search_fields = ('name', 'description')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.image.url)
        return "Нет изображения"
    image_preview.short_description = 'Превью'

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('external_id', 'first_name', 'last_name', 'phone_number', 'GDPR_status_display')
    list_filter = ('GDPR_status',)
    search_fields = ('first_name', 'last_name', 'phone_number', 'external_id', 'tg_username')
    readonly_fields = ('external_id',)
    
    def GDPR_status_display(self, obj):
        if obj.GDPR_status:
            return format_html('<span style="color: green;">✓ Согласие получено</span>')
        return format_html('<span style="color: red;">✗ Согласия нет</span>')
    GDPR_status_display.short_description = 'GDPR статус'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'properties_count')
    search_fields = ('product_name',)
    
    def properties_count(self, obj):
        return obj.product_properties_set.count()
    properties_count.short_description = 'Количество свойств'

@admin.register(Product_properties)
class ProductPropertiesAdmin(admin.ModelAdmin):
    list_display = ('product', 'property_name', 'parameters_count')
    list_filter = ('product',)
    search_fields = ('property_name', 'product__product_name')
    
    def parameters_count(self, obj):
        return obj.product_parameters_set.count()
    parameters_count.short_description = 'Количество параметров'

@admin.register(Product_parameters)
class ProductParametersAdmin(admin.ModelAdmin):
    list_display = ('product_property', 'parameter_name', 'parameter_price', 'full_property_path')
    list_filter = ('product_property__product', 'product_property')
    search_fields = ('parameter_name', 'product_property__property_name')
    list_editable = ('parameter_price',)
    
    def full_property_path(self, obj):
        return f"{obj.product_property.product.product_name} → {obj.product_property.property_name}"
    full_property_path.short_description = 'Полный путь'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'customer', 'order_status', 'order_price', 
        'delivery_date', 'delivery_time', 'phone', 'email'
    )
    list_filter = ('order_status', 'order_type', 'delivery_date')
    search_fields = ('customer', 'delivery_address', 'phone', 'email')
    readonly_fields = (
        'levels', 'form', 'topping', 'berries', 'decor', 
        'words', 'order_comments', 'phone', 'email', 'order_details'
    )
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('customer', 'phone', 'email', 'order_status', 'order_price')
        }),
        ('Детали заказа', {
            'fields': ('levels', 'form', 'topping', 'berries', 'decor', 'words', 'order_comments')
        }),
        ('Доставка', {
            'fields': ('delivery_address', 'delivery_date', 'delivery_time', 'comments')
        }),
        ('Системная информация', {
            'fields': ('order_details', 'order_type', 'cake_name')
        }),
    )    

    def customer_display(self, obj):
        return obj.customer or "Не указан"
    customer_display.short_description = 'Покупатель'
    
    def order_status_display(self, obj):
        status_colors = {
            'Заявка обрабатывается': 'orange',
            'Готовим ваш торт': 'blue',
            'Продукт в пути': 'purple',
            'Продукт у вас': 'green'
        }
        color = status_colors.get(obj.order_status, 'gray')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.order_status)
    order_status_display.short_description = 'Статус'
    
    def delivery_info(self, obj):
        if obj.delivery_date and obj.delivery_time:
            return f"{obj.delivery_date} {obj.delivery_time.strftime('%H:%M')}"
        return "Не указано"
    delivery_info.short_description = 'Доставка'
    
    def order_type_display(self, obj):
        type_icons = {
            'Собрать свой торт': '🛠️',
            'Заказать торт': '🎂'
        }
        return f"{type_icons.get(obj.order_type, '')} {obj.order_type}"
    order_type_display.short_description = 'Тип заказа'
    
    def created_at(self, obj):
        return obj.created if hasattr(obj, 'created') else 'Неизвестно'
    created_at.short_description = 'Создан'
    
    def updated_at(self, obj):
        return obj.updated if hasattr(obj, 'updated') else 'Неизвестно'
    updated_at.short_description = 'Обновлен'
