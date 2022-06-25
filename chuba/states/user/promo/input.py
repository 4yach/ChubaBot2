
from chuba.bot import Chuba

from chuba.state import (
    button,
    message,
    StateContext,
    MessageEvent,
    DiscordMessageState,
    DiscordMessageStateForm)
from chuba.buttons import AnyUserButtons


class UserMenuPromoForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "UserMenuPromo")


class UserMenuPromo(DiscordMessageState):

    """Оформление промокода

    В этой форме ползователю требуется ввести промокод для
    дальнешей регистрации.

    """

    form = UserMenuPromoForm()

    @button(custom_id=AnyUserButtons.ANY_GOBACK)
    async def go_back(self, ctx: StateContext):
        await ctx.set("UserMenu")

    @message()
    async def handle_promo(self, ctx: StateContext):
        event = ctx.event
        user_id = ctx.user.id

        if isinstance(event, MessageEvent):
            promo: str = event.message.content
            promo_holder = Chuba.promo_storage.find_containing_promo_holder(promo)

            if promo_holder and await Chuba.user_db.try_register_promo(promo, user_id):
                Chuba.dispatch("promo_received", promo, promo_holder.role, user_id)
                await ctx.set("UserPromoSuccess")
            else:
                await ctx.set("UserPromoFailed")

