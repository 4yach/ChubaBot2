
from os.path import exists

from chuba.log import log
from chuba.bot import ChubaBot
from chuba.config import Configuration

from discord.ext.commands import Cog


class ConfigCog(Cog):

    def __init__(self, bot: ChubaBot, config_path: str):
        self._bot: ChubaBot = bot
        self._config_path = config_path

    @Cog.listener()
    async def on_ready(self):
        log.info("Инициализация конфигурации бота")

        if exists(self._config_path):
            self._bot.config = Configuration.load(self._config_path)
        else:
            log.error(f"Файл конфигурации не был найден '{self._config_path}'")
