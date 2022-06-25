
from discord import User, Guild, Member
from discord_components import Select, SelectOption

from chuba.bot import Chuba

from chuba.state import (
    button,
    select,
    message,
    StateEvent,
    StateContext,
    MessageEvent,
    SelectEvent,
    DiscordMessageState,
    DiscordMessageStateForm)
from chuba.users import UserModel
from chuba.buttons import AnyUserButtons, UserButtons
from chuba.selects import AdminSelects


class AdminPromoAmountForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "AdminPromoAmount")


class AdminPromoAmount(DiscordMessageState):

    """Ввод количества промокодов
    """

    form = AdminPromoAmountForm()

    @message()
    async def handle_promo_amount(self, ctx: StateContext):
        event = ctx.event

        if isinstance(event, MessageEvent):
            content: str = event.message.content

            if content.isdigit():
                with ctx.data() as data:
                    data["Amount"] = int(content)
                await ctx.set("AdminPromoDays")
            else:
                pass

    @button(custom_id=AnyUserButtons.ANY_GOBACK)
    async def go_back(self, ctx: StateContext):
        await ctx.set("AdminMenu")
