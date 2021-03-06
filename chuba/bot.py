
from sys import exc_info
from uuid import uuid4
from discord import Intents

from aiohttp.web import Application

from chuba.state import StateMachine
from chuba.promo import PromoStorage
from chuba.users import UsersDatabase
from chuba.config import Configuration

from chuba.payment.anymoney import AnyMoney
from chuba.payment.cloudpayments import CloudPayments

from discord.ext.commands import Bot


class ChubaBot(Bot):

    config: Configuration
    """Ссылка на объект текущего конфига
    """

    user_db: UsersDatabase
    """Ссылка на объект текущей базы данных пользователей
    """

    webhook: Application

    am_client: AnyMoney

    cp_client: CloudPayments

    usdt_excrate: int

    state_machine: StateMachine
    """Ссылка на объект текущей машины состояний
    """

    promo_storage: PromoStorage
    """Ссылка на объект текущей базы промокодов
    """

    @property
    def crypto_sub_amount(self) -> int:
        return round(self.config.get_value("server_specific", "sub_usdt_rate") / self.usdt_excrate)

    @property
    def crypto_vip_amount(self) -> int:
        return round(self.config.get_value("server_specific", "vip_usdt_rate") / self.usdt_excrate)

    async def on_error(self, event_method, *args, **kwargs):
        if event_method != "error_caught":
            self.dispatch(
                "error_caught",
                exc_info(),
                uuid4(),
                event_method,
                *args, **kwargs)


Chuba = ChubaBot(command_prefix='/', intents=Intents.all())
