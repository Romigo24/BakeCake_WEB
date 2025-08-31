import uuid
from yookassa import Configuration, Payment
from django.conf import settings


Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


def create_payment(order, return_url):
    idempotence_key = str(uuid.uuid4())
    
    payment = Payment.create({
        "amount": {
            "value": f"{order.total_price:.2f}",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": return_url
        },
        "metadata": {
            "order_id": order.id
        },
        "description": f"Заказ №{order.id}",
        "capture": True
    }, idempotence_key)
    
    return payment


def check_payment_status(payment_id):
    """
    Проверка статуса платежа
    """
    payment = Payment.find_one(payment_id)
    return payment.status