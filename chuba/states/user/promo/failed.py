
from chuba.bot import Chuba

from chuba.state import (
    button,
    StateContext,
    DiscordMessageState,
    DiscordMessageStateForm)
from chuba.buttons import AnyUserButtons, UserButtons


class UserPromoFailedForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "UserPromoFailed")


class UserPromoFailed(DiscordMessageState):

    form = UserPromoFailedForm()

    @button(custom_id=AnyUserButtons.ANY_GOBACK)
    async def go_menu(self, ctx: StateContext):
        await ctx.set("UserMenu")

    @button(custom_id=UserButtons.PROMO_RETRY)
    async def go_back(self, ctx: StateContext):
        await ctx.set("UserMenuPromo")
