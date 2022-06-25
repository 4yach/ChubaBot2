
from discord import Embed

from chuba.bot import Chuba
from chuba.state import (
    button,
    StateContext,
    StateEventType,
    DiscordMessageState,
    DiscordMessageStateForm)
from chuba.buttons import AnyUserButtons


class AnyStartForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "AnyStart")


class AnyStart(DiscordMessageState):

    """Начальное состояние для каждого пользователя

    Начальное состояния, которое выводится независимо от того,
    является пользователь администратором или нет. В данном
    состоянии отображается информация об обновлении бота.

    """

    form = AnyStartForm()

    @button(custom_id=AnyUserButtons.START_GOTIT)
    async def got_it(self, ctx: StateContext):
        _user_id: int = ctx.user.id

        if _user_id in Chuba.config.get_value("server_specific", "admins"):
            await ctx.set("AdminMenu")
        else:
            await ctx.set("UserOffer")
