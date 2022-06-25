
from discord import User, Guild, Member

from chuba.bot import Chuba

from chuba.state import (
    button,
    StateContext,
    DiscordMessageState,
    DiscordMessageStateForm)
from chuba.buttons import AnyUserButtons


class AdminUserUnknownForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "AdminUserUnknown")


class AdminUserUnknown(DiscordMessageState):

    """Ввод количества промокодов
    """

    form = AdminUserUnknownForm()

    @button(custom_id=AnyUserButtons.ANY_GOBACK)
    async def go_back(self, ctx: StateContext):
        await ctx.set("AdminMenu")
