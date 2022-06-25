
from enum import Enum
from discord import Member, User
from discord_components import Interaction

from discord.ext.commands import Context


class StateEventType(Enum):
    """Перечисление типов событий
    """


class StateEvent:
    """Базовый класс события состояний
    """

    type: StateEventType
    """Тип события
    """

    user: Member | User
    """Пользователь, который вызвал данное событие
    """

    def matches(self, filters) -> bool:
        return True
