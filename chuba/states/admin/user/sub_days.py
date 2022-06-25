
from chuba.bot import Chuba

from chuba.state import (
    button,
    message,
    StateContext,
    MessageEvent,
    DiscordMessageState,
    DiscordMessageStateForm)
from chuba.buttons import AnyUserButtons


class AdminUserInfoDaysForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "AdminUserInfoDays")


class AdminUserInfoDays(DiscordMessageState):

    """Ввод количества промокодов
    """

    form = AdminUserInfoDaysForm()

    @message()
    async def handle_user_id(self, ctx: StateContext):
        event = ctx.event

        if isinstance(event, MessageEvent):
            content: str = event.message.content

            if content.isdigit():
                with ctx.data() as data:
                    Chuba.dispatch("subscription_payed", data["Sub"], int(content), data["UserId"])
                await ctx.set("AdminUserInfo")

    @button(custom_id=AnyUserButtons.ANY_GOBACK)
    async def go_back(self, ctx: StateContext):
        await ctx.set("AdminMenu")
