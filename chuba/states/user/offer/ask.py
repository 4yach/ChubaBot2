
from chuba.bot import Chuba

from chuba.state import (
    button,
    StateContext,
    DiscordMessageState,
    DiscordMessageStateForm)

from chuba.buttons import UserButtons


class UserOfferForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "UserOffer")


class UserOffer(DiscordMessageState):

    form = UserOfferForm()

    @button(custom_id=UserButtons.OFFER_ACCEPT)
    async def accept_offer(self, ctx: StateContext):
        await Chuba.user_db.create_user(ctx.user.id)
        await ctx.set("UserMenu")

    @button(custom_id=UserButtons.OFFER_DECLINE)
    async def decline_offer(self, ctx: StateContext):
        await ctx.set("UserOfferDeclined")
