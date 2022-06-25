
"""

Мнимальный API для работы с CloudPayments

"""

from aiohttp import ClientSession, BasicAuth

from chuba.utils import utcnow_ms
from chuba.payment.types import PaymentBase
from chuba.payment.endpoints import Endpoints


class CloudPayments(PaymentBase):
    """Класс для работы с платежным сервисом CloudPayments

    """

    endpoint = Endpoints.CLOUD_PAYMENTS

    def __init__(self, public_id, api_secret, ):
        self._basic_auth = BasicAuth(public_id, api_secret)

    async def call_method(self, method, params=None):
        _headers = {
            "X-Request-ID": str(utcnow_ms())
        }
        async with ClientSession(auth=self._basic_auth) as cs:
            async with cs.post(url=self.endpoint + method, json=params, headers=_headers) as _resp:
                _result = await _resp.json()
        return _result

    async def create(self, invoice_id: str, **kwargs) -> dict:
        """Создание платежа

        Создание платежа (Через email, но емейл опущен в данной задаче) внутри системы CloudPayments

        :param amount: Сумма
        :param description: Описание
        :param invoice_id: id в рамках этого проекта
        :return: Model
        """
        return await self.call_method(
            "orders/create",
            {
                'Amount': kwargs.pop("amount"),
                'Description': kwargs.pop("description"),
                'InvoiceId': invoice_id
            }
        )

    async def check(self, invoice_id: str) -> dict:
        """Проверка платежа
        :param invoice_id: 
        :return: True, если платеж совершен, иначе False
        """
        return await self.call_method(
            "payments/find",
            {
                'InvoiceId': invoice_id
            }
        )

    async def cancel(self, invoice_id: str) -> dict:
        """Отмена платежа по invoice id в системе CloudPayments

        :param invoice_id: ID счета
        :return: Ответ сервера
        """
        return await self.call_method(
            "orders/cancel",
            {
                'Id': invoice_id
            }
        )
