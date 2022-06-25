
from discord import Message
from discord_components import Interaction

from chuba.state.event import StateEvent, StateEventType


class DiscordStateEventType(StateEventType):
    BUTTON = 0
    SELECT = 1
    MESSAGE = 2


class ButtonEvent(StateEvent):
    type: StateEventType = DiscordStateEventType.BUTTON

    def __init__(self, interaction: Interaction):
        self.user = interaction.user
        self.interaction = interaction

    def matches(self, filters) -> bool:
        return self.interaction.custom_id == filters.get("custom_id", 0)


class SelectEvent(StateEvent):
    type: StateEventType = DiscordStateEventType.SELECT

    def __init__(self, interaction: Interaction):
        self.user = interaction.user
        self.interaction = interaction

    def matches(self, filters) -> bool:
        return self.interaction.custom_id == filters.get("custom_id", 0)


class MessageEvent(StateEvent):
    type: StateEventType = DiscordStateEventType.MESSAGE

    def __init__(self, message: Message):
        self.user = message.author
        self.message = message
