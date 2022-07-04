
from json import loads, dumps
from datetime import datetime
from pydantic import BaseModel
from pydantic.utils import to_camel


class AnyMoneyModel(BaseModel):
    class Config:
        json_loads = loads
        json_dumps = dumps
        json_encoders = {datetime: lambda dt: int(dt.timestamp())}
        alias_generator = to_camel
        allow_population_by_field_name = True


class CallbackModel(AnyMoneyModel):
    account_amount: int
    """Сумма зачисления, за вычетом комиссии
    """

    ctime: int
    """Время создания ордера
    """

    ftime: int
    """Время финализирования ордера
    """

    in_amount: int
    """Сумма пополнения
    """

    in_curr: str
    """Валюта пополнения
    """

    lid: int
    """Локальный ID ордера
    """

    out_amount: int
    """Сумма зачисления
    """

    out_curr: str
    """Валюта зачисления
    """

    payway_name: str | None = None
    """Наименование платежной среды
    """

    status: str
    """Статус платежа
    """

    externalid: str
    """ID, заданный мерчантом
    """
