
from discord_components import DiscordComponents

from chuba.log import log

from discord.ext.commands import Bot, Cog


class DCSetupCog(Cog):

    def __init__(self, bot):
        self.bot: Bot = bot

    @Cog.listener()
    async def on_ready(self):
        log.info("Инициализация DiscordComponents")
        DiscordComponents(self.bot)
