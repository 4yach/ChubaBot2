
from chuba.log import log
from chuba.bot import Chuba, ChubaBot
from chuba.utils import ipv4net
from discord.ext.commands import Cog

from chuba.payment.anymoney import AnyMoney


class AnyMoneyCog(Cog):

    def __init__(self, bot: ChubaBot, api_key: str, merchant_id: int):
        self.bot = bot
        self.loop = bot.loop
        self.api_key = api_key
        self.merchant_id = merchant_id

    @Cog.listener()
    async def on_ready(self):
        log.info("Инициализация Any Money")

        self.bot.am_client = AnyMoney(self.api_key, self.merchant_id)
