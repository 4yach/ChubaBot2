
from typing import Union, Tuple
from datetime import date
from dataclasses import dataclass, field

from chuba.utils import from_iso_8601, to_iso_8601


@dataclass
class UserModel:
    id: int
    """ID пользователя в системе ChubaBot эквивалентен ID пользователя в Discord
    """

    promo: str | None = None
    subscription_raw: str | None = None
    vip_subscription_raw: str | None = None
    last_payment_id: str | None = None

    @property
    def subscription(self):
        return from_iso_8601(self.subscription_raw) if self.subscription_raw else None

    @subscription.setter
    def subscription(self, value: date):
        self.subscription_raw = to_iso_8601(value) if value else None

    @property
    def vip_subscription(self):
        return from_iso_8601(self.vip_subscription_raw) if self.vip_subscription_raw else None

    @vip_subscription.setter
    def vip_subscription(self, value: date):
        self.vip_subscription_raw = to_iso_8601(value) if value else None

    @classmethod
    def from_sql(cls, sql: Tuple) -> Union["UserModel", None]:
        return UserModel(*sql) if sql else None

    def to_sql(self) -> Tuple:
        return self.id,\
               self.promo,\
               self.subscription_raw,\
               self.vip_subscription_raw,\
               self.last_payment_id
