from django.core.exceptions import BadRequest
from yookassa import Configuration, Payment, Refund
import os
import uuid


class YandexPayment:
    def __init__(self):
        Configuration.account_id = os.getenv('YOOKASSA_ACCOUNT_ID')
        Configuration.secret_key = os.getenv('YOOKASSA_SECRET_KEY')
        self.idempotence_key = str(uuid.uuid4())

    def create_payment(self, price: str, service: str, phone_number: str, person_name: str, user_is_authenticated: bool,
                       user_id: str | None):
        params = {
            "amount": {
                "value": price,
                "currency": "RUB"
            }, "confirmation": {
                "type": "embedded"
            }, "capture": True, "description": service + ' ' + person_name + ' ' + phone_number,
            'merchant_customer_id': user_id if user_is_authenticated else phone_number + ' ' + person_name
        }

        payment = Payment.create(params, self.idempotence_key)
        return payment

    def refund_payment(self, payment_id: str):
        payment = Payment.find_one(payment_id)
        if payment['status'] != 'succeeded':
            return
        refund_response = Refund.create({
            "amount": {
                "value": payment['amount']['value'],
                "currency": "RUB"
            },
            "payment_id": payment_id
        }, self.idempotence_key)

        if refund_response["status"] == "canceled":
            if refund_response['cancellation_details']['reason'] == 'insufficient_funds':
                raise BadRequest(
                    f"Инициатор ошибки: {refund_response['cancellation_details']['party']}<br>"
                    f'Ошибка: "insufficient_funds"<br>'
                    f'Не хватает денег, чтобы сделать возврат: сумма платежей, которые вы получили в день '
                    f'возврата, меньше, чем сам возврат, или есть задолженность.<br>Пополните баланс '
                    f'обеспечения возвратов в личном кабинете ЮKassa, после этого возвраты снова станут '
                    f'доступны в течение 4 часов.'
                )
            if refund_response['cancellation_details']['reason'] == 'rejected_by_payee':
                raise BadRequest(
                    f"Инициатор ошибки: {refund_response['cancellation_details']['party']}<br>"
                    f'Ошибка: "rejected_by_payee"<br>'
                    f'Эмитент платежного средства или другой участник процесса возврата отклонил операцию '
                    f'по неизвестным причинам. Сделать возврат через ЮKassa нельзя. Предложите пользователю '
                    f'обратиться к эмитенту (например, в банк) для уточнения подробностей и дождитесь '
                    f'ответа:<br>Если причину отмены устранили, повторите возврат'
                    f'.<br>Если проблема осталась, договоритесь с пользователем о том, чтобы '
                    f'вернуть ему деньги напрямую, не через ЮKassa. И свяжитесь с разработчиком для удаления записи из '
                    f'базы данных.'
                )
            if refund_response['cancellation_details']['reason'] == 'rejected_by_timeout':
                raise BadRequest(
                    f"Инициатор ошибки: {refund_response['cancellation_details']['party']}<br>"
                    f'Ошибка: "rejected_by_timeout"<br>'
                    f'Технические неполадки на стороне инициатора отмены возврата. Повторите запрос. Если результат не '
                    f'изменится, повторяйте запрос с возрастающим разумным интервалом (например, можно использовать '
                    f'последовательность Фибоначчи).<br>Если прошло более получаса, но вы всё еще получаете '
                    f'rejected_by_timeout, обратитесь к инициатору отмены возврата для уточнения подробностей.'
                )
            if refund_response['cancellation_details']['reason'] == 'yoo_money_account_closed':
                raise BadRequest(
                    f"Инициатор ошибки: {refund_response['cancellation_details']['party']}<br>"
                    f'Ошибка: "yoo_money_account_closed"<br>'
                    f'Пользователь закрыл кошелек ЮMoney, на который вы пытаетесь вернуть платеж. Сделать возврат через '
                    f'ЮKassa нельзя. Договоритесь с пользователем напрямую, каким способом вы вернете ему деньги. '
                    f'И свяжитесь с разработчиком для удаления записи из базы данных.'
                )
            if refund_response['cancellation_details']['reason'] == 'general_decline':
                raise BadRequest(
                    f"Инициатор ошибки: {refund_response['cancellation_details']['party']}<br>"
                    f'Ошибка: "general_decline"<br>'
                    f'Причина не детализирована. Для уточнения подробностей обратитесь в техническую поддержку.'
                )

    @staticmethod
    def amount_value(payment_id):
        payment = Payment.find_one(payment_id)
        return payment['amount']['value']