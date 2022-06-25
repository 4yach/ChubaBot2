
from chuba.bot import Chuba

from chuba.state import (
    button,
    StateContext,
    DiscordMessageState,
    DiscordMessageStateForm)
from chuba.buttons import AdminButtons


class AdminPromoConfirmForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "AdminPromoConfirm")


class AdminPromoConfirm(DiscordMessageState):

    """Подтверждение создания промокодов
    """

    form = AdminPromoConfirmForm()

    @button(custom_id=AdminButtons.ADMIN_CONFIRM_YES)
    async def confirm_promos(self, ctx: StateContext):
        await ctx.set("AdminPromoCreate")

    @button(custom_id=AdminButtons.ADMIN_CONFIRM_NO)
    async def decline_promos(self, ctx: StateContext):
        await ctx.set("AdminMenu")
