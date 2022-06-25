
from chuba.bot import Chuba

from chuba.state import (
    button,
    message,
    MessageEvent,
    StateContext,
    DiscordMessageState,
    DiscordMessageStateForm)

from chuba.selects import UserSelects
from chuba.buttons import AnyUserButtons


class InputVipAmountForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "InputVipAmount")


class InputVipAmount(DiscordMessageState):

    form = InputVipAmountForm()

    @message()
    async def handle_amount(self, ctx: StateContext):
        event = ctx.event

        if isinstance(event, MessageEvent):
            with ctx.data() as data:
                data["Days"] = Chuba.config.get_value("server_specific", "vipsub_days")
                data["Amount"] = event.message.content
            await ctx.set("PaymentConfirm")

    @button(custom_id=AnyUserButtons.ANY_GOBACK)
    async def go_back(self, ctx: StateContext):
        await ctx.set("UserMenu")
