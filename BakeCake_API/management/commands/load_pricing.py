from django.core.management.base import BaseCommand
from webapp.models import Product, Product_properties, Product_parameters
from BakeCake_API.pricing import OPTIONS

class Command(BaseCommand):
    help = 'Load pricing data from pricing.py into database'
    
    def handle(self, *args, **options):
        self.stdout.write('Загрузка данных из pricing.py...')
        
        # Создаем основной продукт "Торт"
        cake_product, created = Product.objects.get_or_create(
            product_name="Торт"
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Создан продукт: Торт'))
        
        # Загружаем все свойства
        properties_mapping = {
            "Уровни": ("Levels", OPTIONS["Levels"]),
            "Форма": ("Forms", OPTIONS["Forms"]),
            "Топпинг": ("Toppings", OPTIONS["Toppings"]),
            "Ягоды": ("Berries", OPTIONS["Berries"]),
            "Декор": ("Decors", OPTIONS["Decors"]),
        }
        
        for prop_name, (option_key, option_data) in properties_mapping.items():
            self.load_property(cake_product, prop_name, option_key, option_data)
        
        self.stdout.write(self.style.SUCCESS('Данные успешно загружены!'))
    
    def load_property(self, product, property_name, option_key, option_data):
        property_obj, created = Product_properties.objects.get_or_create(
            product=product,
            property_name=property_name
        )
        
        if created:
            self.stdout.write(f"Создано свойство: {property_name}")
        
        # Загружаем параметры
        for i, (value, price) in enumerate(zip(option_data["values"], option_data["prices"])):
            # Пропускаем нулевые/пустые значения
            if i == 0 and value.lower() in ['не выбрано', 'нет', 'без', '']:
                continue
                
            param, created = Product_parameters.objects.get_or_create(
                product_property=property_obj,
                parameter_name=value,
                defaults={'parameter_price': price}
            )
            
            if created:
                self.stdout.write(f"  - {value}: {price}₽")