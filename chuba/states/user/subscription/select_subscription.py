
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


class SelectSubscriptionForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "SelectSubscription")


class SelectSubscription(DiscordMessageState):

    form = SelectSubscriptionForm()

    @select(custom_id=UserSelects.USER_SUBSCRIPTION_SELECT)
    async def select_currency(self, ctx: StateContext):
        event = ctx.event

        if isinstance(event, SelectEvent):
            subscription = event.interaction.values[0]

            with ctx.data() as data:
                data["Subscription"] = subscription

            match subscription:
                case "SUB":
                    await ctx.set("SelectSubscriptionPlan")
                case "VIP":
                    await ctx.set("InputVipAmount")

    @button(custom_id=AnyUserButtons.ANY_GOBACK)
    async def go_back(self, ctx: StateContext):
        await ctx.set("UserMenu")
