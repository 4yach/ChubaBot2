
from asyncio import ensure_future

from aiohttp.web import Application, TCPSite, AppRunner
from chuba.log import log
from chuba.bot import Chuba, ChubaBot
from discord.ext.commands import Cog


class WebhookCog(Cog):

    app: Application

    def __init__(self, bot: ChubaBot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        log.info("Инициализация вебхука")

        self.app = self.bot.webhook = Application()


class WebhookStarterCog(Cog):

    runner: AppRunner

    def __init__(self, bot: ChubaBot, ip_addr: str, port: int):
        self.bot = bot
        self.loop = bot.loop
        self.port = port
        self.ip_addr = ip_addr

    async def _run_app(self, app_runner: AppRunner):
        await app_runner.setup()
        self.site = TCPSite(app_runner, self.ip_addr, self.port)
        await self.site.start()

    def cog_unload(self):
        ensure_future(self.site.stop())

    @Cog.listener()
    async def on_ready(self):
        log.info("Запуск вебхука")

        self.runner = AppRunner(self.bot.webhook)
        self.loop.create_task(self._run_app(self.runner))
