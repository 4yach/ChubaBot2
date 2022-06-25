
from chuba.bot import Chuba

from chuba.state import (
    button,
    StateContext,
    DiscordMessageState,
    DiscordMessageStateForm)

from chuba.buttons import UserButtons


class UserOfferDeclineForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "UserOfferDeclined")


class UserOfferDeclined(DiscordMessageState):

    form = UserOfferDeclineForm()

    @button(custom_id=UserButtons.OFFER_REACCEPT)
    async def reaccept_offer(self, ctx: StateContext):
        await ctx.set("UserOffer")
