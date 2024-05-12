from yookassa import Configuration, Payment
import os
import uuid


class YandexPayment:
    def __init__(self):
        Configuration.account_id = os.getenv('YOOKASSA_TEST_ACCOUNT_ID')
        Configuration.secret_key = os.getenv('YOOKASSA_TEST_SECRET_KEY')
        self.idempotence_key = str(uuid.uuid4())

    def create_payment(self, price: str, service: str):
        payment = Payment.create({
            "amount": {
                "value": price,
                "currency": "RUB"
            },
            "confirmation": {
                "type": "embedded"
            },
            "capture": True,
            "description": service
        }, self.idempotence_key)
        return payment
