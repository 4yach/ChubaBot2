
from chuba.bot import Chuba

from chuba.state import (
    button,
    message,
    StateContext,
    MessageEvent,
    DiscordMessageState,
    DiscordMessageStateForm)
from chuba.buttons import AnyUserButtons


class AdminUserPromoRoleForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "AdminUserPromoRole")


class AdminUserPromoRole(DiscordMessageState):

    """Ввод роли, которую будет присваивать именной промокод
    """

    form = AdminUserPromoRoleForm()

    @message()
    async def handle_user_id(self, ctx: StateContext):
        event = ctx.event
        if isinstance(event, MessageEvent):
            with ctx.data() as data:
                promo = data["Promo"]
                async with Chuba.user_db.user(data["UserId"]) as user_model:
                    user_model.promo = promo
                Chuba.dispatch("promo_received", promo, event.message.content, ctx.user.id)
            await ctx.set("AdminUserInfo")

    @button(custom_id=AnyUserButtons.ANY_GOBACK)
    async def go_back(self, ctx: StateContext):
        await ctx.set("AdminUserInfo")
