
from chuba.bot import Chuba

from chuba.state import (
    button,
    StateContext,
    DiscordMessageState,
    DiscordMessageStateForm)

from chuba.buttons import AnyUserButtons


class UserPromoSuccessForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "UserPromoSuccess")


class UserPromoSuccess(DiscordMessageState):

    form = UserPromoSuccessForm()

    @button(custom_id=AnyUserButtons.ANY_GOBACK)
    async def go_menu(self, ctx: StateContext):
        await ctx.set("UserMenu")
