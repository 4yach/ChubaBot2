
from time import time

from hmac import (
    new as hmac_new,
    HMAC)

from hashlib import sha512

from aiohttp import ClientSession

from chuba.utils import utcnow_ms
from chuba.payment.types import PaymentBase
from chuba.payment.endpoints import Endpoints


class AnyMoney(PaymentBase):
    """
    Класс с полезными методами для работы с API сервиса Any.Money
    """

    endpoint: str = Endpoints.ANY_MONEY

    def __init__(self, api_key, merchant):
        self._api_key = api_key
        self._merchant = merchant

    def _sign(self, data: dict, utcs_now: str) -> str:
        # закодируем ключ API сразу
        _api_key = self._api_key.encode()
        # словарь должен быть отсортирован
        if data:
            data = sorted(data.items())
        # формируем строку из значений data без вложенный объектов и null
        _message = ''
        for _, val in data:
            # избавляемся от вложенностей и null
            if not isinstance(val, (dict, list, type(None))):
                _message += str(val)
        _message = _message.lower() + utcs_now
        _message = _message.encode()
        # применяем алгоритм sha512 к запросу
        _hmac_o: HMAC = hmac_new(
            _api_key,
            _message,
            sha512)
        return _hmac_o.hexdigest()

    async def call_method(self, method: str, params: dict) -> dict:
        """
        Вызываем RPC методы сервиса Any.Money

        :param str method: имя метода, который нужно вызвать (Например: invoice.create)
        :param dict params: словарь с параметрами, без вложенностей, без массивов и None
        :return dict: JSON ответ
        """
        # формируем заголовки
        _utc: str = str(utcnow_ms())
        _headers = {
            "x-merchant": self._merchant,
            "x-signature": self._sign(params, _utc),
            "x-utc-now-ms": _utc
        }
        # формируем данные
        _data = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": "1"
        }
        async with ClientSession() as cs:
            async with cs.post(url=self.endpoint, json=_data, headers=_headers) as _resp:
                return await _resp.json()

    async def create(self, invoice_id: str, **kwargs) -> dict:
        """
        Создать инвойс (ордер) для оплаты в определенной валюте и
        до определенного срока.
        :param str invoice_id: уникальный номер мерчанта
        :param str currency: валюта, в которой будет произведена оплата
        :param str amount: счет, например 3002,10
        :params str email: почта клиента, куда придет оповещение об операции
        :param str lifetime: время активности ордера
        :return dict: ответ сервера
        """
        return await self.call_method(
            "invoice.create",
            {
                "externalid": invoice_id,
                "amount": kwargs.pop("amount"),
                "in_curr": kwargs.pop("currency"),
                "lifetime": kwargs.pop("lifetime"),
                "is_multipay": True
            }
        )

    async def check(self, merchant_id: str) -> dict:
        """
        Получать данные ордера по его идентификатору.
        :param: str external_id: уникальный идентификатор ордера, заданный мерчантом
        :return dict: ответ сервера
        """
        return await self.call_method(
            "status",
            {
                "externalid": merchant_id
            })

    async def cancel(self, *args) -> dict:
        """
        Не реализован
        """
        return {}
