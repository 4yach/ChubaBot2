
from datetime import date, timedelta

from chuba.log import log
from chuba.bot import ChubaBot
from chuba.users import UsersDatabase

from discord.ext.tasks import loop
from discord.ext.commands import Cog


class DatabaseCog(Cog):

    db: UsersDatabase

    def __init__(self, bot: ChubaBot, usersdb_path: str):
        self._bot = bot
        self._usersdb_path = usersdb_path

    @Cog.listener()
    async def on_ready(self):
        log.info("Инициализация базы данных пользователей")

        self.db = self._bot.user_db = UsersDatabase(self._usersdb_path)
        await self.db.setup()

        self.check_expiried_subscriptions.start()
        self.check_expiried_vipsubscriptions.start()

    @Cog.listener()
    async def on_promo_declined(self, user_id: int):
        async with self.db.user(user_id) as user_model:
            user_model.promo = None
        log.info(f"Отменен промокод для пользователя {user_id}")

    @Cog.listener()
    async def on_subscription_payed(self, subscription, days, user_id, amount, currency):
        async with self.db.user(user_id) as user_model:
            match subscription:
                case "SUB":
                    user_model.subscription = (user_model.subscription or date.today()) + timedelta(days=days)
                case "VIP":
                    user_model.vip_subscription = (user_model.vip_subscription or date.today()) + timedelta(days=days)

            log.info(f"{user_id} оплатил/получил подписку {subscription} на {days} дней в размере {amount} {currency}")

    @Cog.listener()
    async def on_subscription_declined(self, subscription, user_id):
        async with self.db.user(user_id) as user_model:
            match subscription:
                case "SUB":
                    user_model.subscription = None
                case "VIP":
                    user_model.vip_subscription = None

            log.info(f"Отменена подписка {subscription} для {user_id}")

    @loop(hours=24)
    async def check_expiried_subscriptions(self):
        log.info("Обработка просроченных подписок каждые сутки")

        for user_raw in await self.db.get_expiried_subscriptions():
            log.info(f"Подписка пользователя {user_raw[0]} просрочена")
            self._bot.dispatch("subscription_declined", "SUB", user_raw[0])

    @loop(hours=24)
    async def check_expiried_vipsubscriptions(self):
        log.info("Обработка просроченных ВИП подписок каждые сутки")

        for user_raw in await self.db.get_expiried_vipsubscriptions():
            log.info(f"ВИП подписка пользователя {user_raw[0]} просрочена")
            self._bot.dispatch("subscription_declined", "VIP", user_raw[0])
