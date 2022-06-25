
from discord import User, Guild, Member

from chuba.bot import Chuba

from chuba.state import (
    button,
    message,
    StateContext,
    MessageEvent,
    DiscordMessageState,
    DiscordMessageStateForm)
from chuba.buttons import AnyUserButtons


class AdminUserInfoIdForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "AdminUserInfoId")


class AdminUserInfoId(DiscordMessageState):

    """Ввод количества промокодов
    """

    form = AdminUserInfoIdForm()

    @message()
    async def handle_user_id(self, ctx: StateContext):
        event = ctx.event

        if isinstance(event, MessageEvent):
            content: str = event.message.content

            if content.isdigit():
                user_id = int(content)
                user_model = await Chuba.user_db.get_user(user_id)
                if not user_model:
                    await ctx.set("AdminUserUnknown")
                else:
                    with ctx.data() as data:
                        data["UserId"] = user_id
                        data["UserModel"] = user_model
                    await ctx.set("AdminUserInfo")
            else:
                pass

    @button(custom_id=AnyUserButtons.ANY_GOBACK)
    async def go_back(self, ctx: StateContext):
        await ctx.set("AdminMenu")
