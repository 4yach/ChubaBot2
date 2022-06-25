
from typing import Dict, Any

from chuba.bot import Chuba

from chuba.state import (
    button,
    select,
    SelectEvent,
    StateContext,
    DiscordMessageState,
    DiscordMessageStateForm)

from chuba.selects import UserSelects
from chuba.buttons import AnyUserButtons


class SelectCurrencyForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "SelectCurrency")


class SelectCurrency(DiscordMessageState):

    form = SelectCurrencyForm()

    @select(custom_id=UserSelects.USER_CURRENCY_SELECT)
    async def select_currency(self, ctx: StateContext):
        event = ctx.event

        with ctx.data() as data:
            if isinstance(event, SelectEvent):
                data["Currency"] = event.interaction.values[0]

        await ctx.set("SelectSubscription")

    @button(custom_id=AnyUserButtons.ANY_GOBACK)
    async def go_back(self, ctx: StateContext):
        await ctx.set("UserMenu")
