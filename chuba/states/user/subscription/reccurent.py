
from chuba.bot import Chuba

from chuba.utils import randseq7

from chuba.state import (
    button,
    MessageEvent,
    StateContext,
    DiscordMessageState,
    DiscordMessageStateForm)

from chuba.buttons import UserButtons


class PaymentRecurrentForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "PaymentRecurrent")


class PaymentRecurrent(DiscordMessageState):

    form = PaymentRecurrentForm()

    @button(custom_id=UserButtons.USER_RECURRENT_CONFIRM)
    async def reccurent_confirm(self, ctx: StateContext):
        with ctx.data() as data:
            data["Reccurent"] = "CreateMonthly"
        await ctx.set("CloudPaymentsView")

    @button(custom_id=UserButtons.USER_RECURRENT_REFUSE)
    async def reccurent_refuse(self, ctx: StateContext):
        await ctx.set("CloudPaymentsView")
