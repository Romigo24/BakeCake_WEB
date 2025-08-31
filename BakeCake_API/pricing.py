from datetime import datetime, timedelta


def is_urgent_order(delivery_date, delivery_time):
    if not delivery_date or not delivery_time:
        return False
    
    delivery_datetime = datetime.combine(delivery_date, delivery_time)
    current_datetime = datetime.now()
    
    return (delivery_datetime - current_datetime) <= timedelta(hours=24)

OPTIONS = {
    "Levels": {
        "values": ['не выбрано', '1', '2', '3'],
        "prices": [0, 400, 750, 1100]
    },
    "Forms": {
        "values": ['не выбрано', 'Круг', 'Квадрат', 'Прямоугольник'],
        "prices": [0, 600, 400, 1000]
    },
    "Toppings": {
        "values": [
            'не выбрано', 'Без', 'Белый соус', 'Карамельный',
            'Кленовый', 'Черничный', 'Молочный шоколад', 'Клубничный'
        ],
        "prices": [0, 0, 200, 180, 200, 300, 350, 200]
    },
    "Berries": {
        "values": ['нет', 'Ежевика', 'Малина', 'Голубика', 'Клубника'],
        "prices": [0, 400, 300, 450, 500]
    },
    "Decors": {
        "values": [
            'нет', 'Фисташки', 'Безе', 'Фундук',
            'Пекан', 'Маршмеллоу', 'Марципан'
        ],
        "prices": [0, 300, 400, 350, 300, 200, 280]
    },
    "Words": 500,
}


def calc_total(details: dict, delivery_date=None, delivery_time=None) -> int:

    def get_index(option_key: str) -> int:
        return int(details.get(option_key, "0") or 0)

    total_price = 0

    total_price += OPTIONS["Levels"]["prices"][get_index("Levels")]
    total_price += OPTIONS["Forms"]["prices"][get_index("Form")]
    total_price += OPTIONS["Toppings"]["prices"][get_index("Topping")]
    total_price += OPTIONS["Berries"]["prices"][get_index("Berries")]
    total_price += OPTIONS["Decors"]["prices"][get_index("Decor")]

    if (details.get("Words") or "").strip():
        total_price += OPTIONS["Words"]

    if delivery_date and delivery_time and is_urgent_order(delivery_date, delivery_time):
        urgent_surcharge = int(total_price * 0.2)
        total_price += urgent_surcharge
    else:
        urgent_surcharge = 0

    return total_price
