
from discord import Message
from discord_components import Interaction

from chuba.log import log
from chuba.bot import ChubaBot
from chuba.state import ButtonEvent, SelectEvent, MessageEvent

from discord.ext.commands import Cog


class EventCog(Cog):

    def __init__(self, bot):
        self.bot: ChubaBot = bot

    async def _handle_event(self, event):
        await self.bot.state_machine.handle_event(event)

    @Cog.listener()
    async def on_ready(self):
        log.info("Инициализация обработчика событий")

    @Cog.listener()
    async def on_message(self, message: Message):
        await self._handle_event(MessageEvent(message))

    @Cog.listener()
    async def on_button_click(self, interaction: Interaction):
        await self._handle_event(ButtonEvent(interaction))

    @Cog.listener()
    async def on_select_option(self, interaction: Interaction):
        await self._handle_event(SelectEvent(interaction))
