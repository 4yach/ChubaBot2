
from stackprinter import format

from chuba.log import log

from discord.ext.commands import Bot, Cog


class DevErrorCog(Cog):

    def __init__(self, bot):
        self.bot: Bot = bot

    @Cog.listener()
    async def on_error_caught(self, exc_info, uuid, event_name, *_args, **_kwargs):
        log.error(f"{format(exc_info)}\nINFO: {event_name} - {uuid}")
