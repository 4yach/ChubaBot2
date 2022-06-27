
from chuba.bot import Chuba

from chuba.state import (
    button,
    message,
    StateContext,
    MessageEvent,
    DiscordMessageState,
    DiscordMessageStateForm)
from chuba.buttons import AnyUserButtons


class AdminUserPromoForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "AdminUserPromo")


class AdminUserPromo(DiscordMessageState):

    """Ввод именного промокода
    """

    form = AdminUserPromoForm()

    @message()
    async def handle_user_id(self, ctx: StateContext):
        event = ctx.event

        if isinstance(event, MessageEvent):
            with ctx.data() as data:
                data["Promo"] = event.message.content
            await ctx.set("AdminUserPromoRole")

    @button(custom_id=AnyUserButtons.ANY_GOBACK)
    async def go_back(self, ctx: StateContext):
        await ctx.set("AdminUserInfo")
