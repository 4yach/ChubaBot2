
from discord import DMChannel, Message
from discord.ext.commands import Cog

from chuba.bot import ChubaBot


class StartCog(Cog):
    
    def __init__(self, bot: ChubaBot):
        self._bot = bot

    @Cog.listener()
    async def on_message(self, message: Message):
        _author = message.author
        _content = message.content.lower()
        _channel = message.channel
        _config = self._bot.config
        _state_machine = self._bot.state_machine
        if isinstance(_channel, DMChannel) and _content in _config.get_value("server_specific", "trigger_words"):
            await _state_machine.set(_author, "AnyStart")
