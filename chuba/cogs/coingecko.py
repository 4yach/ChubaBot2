
from typing import Dict
from aiocoingecko import AsyncCoinGeckoAPISession

from chuba.log import log
from chuba.bot import ChubaBot

from discord.ext.tasks import loop
from discord.ext.commands import Cog


class CoinGeckoCog(Cog):

    def __init__(self, bot: ChubaBot):
        self._bot: ChubaBot = bot

    @Cog.listener()
    async def on_ready(self):
        log.info("Инициализация CoinGecko")
        self.update_usdt_excrate.start()

    @loop(hours=24)
    async def update_usdt_excrate(self):
        log.info("Обновляем курс Тезера")
        async with AsyncCoinGeckoAPISession() as coingecko:
            result: Dict = await coingecko.get_coin_market_chart_by_id(
                days=0,
                coin_id="tether",
                vs_currency="rub")
            self._bot.usdt_excrate = round(result["prices"][0][1])
