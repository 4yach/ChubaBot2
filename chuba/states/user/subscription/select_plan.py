
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


class SelectSubscriptionPlanForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "SelectSubscriptionPlan")


class SelectSubscriptionPlanCryptoForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "SelectSubscriptionPlanCrypto")


class SelectSubscriptionPlan(DiscordMessageState):

    form = SelectSubscriptionPlanForm()
    form_crypto = SelectSubscriptionPlanCryptoForm()

    async def setup(self, ctx: StateContext) -> None:
        form: DiscordMessageStateForm

        with ctx.data() as data:
            currency = data["Currency"]

            match currency:
                case "RUB":
                    form = self.form
                case "USDT":
                    form = self.form_crypto

        await self.show(
            ctx,
            embed=form.embed,
            components=form.component_layout)

    @select(custom_id=UserSelects.USER_PLAN_SELECT)
    async def select_plan(self, ctx: StateContext):
        event = ctx.event

        if isinstance(event, SelectEvent):
            selected_plan = event.interaction.values[0]
            if Chuba.config.has_value("subplans", selected_plan):
                plan = Chuba.config.get_value("subplans", selected_plan)
                with ctx.data() as data:
                    data["Days"] = plan["days"]
                    data["Amount"] = plan["amount"]
                await ctx.set("PaymentConfirm")
            else:
                pass

    @select(custom_id=UserSelects.USER_PLAN_SELECT_CRYPTO)
    async def select_plan_crypto(self, ctx: StateContext):
        event = ctx.event

        if isinstance(event, SelectEvent):
            selected_plan = event.interaction.values[0]
            if Chuba.config.has_value("subplans", selected_plan):
                plan = Chuba.config.get_value("subplans", selected_plan)
                days = plan["days"]
                with ctx.data() as data:
                    data["Days"] = days
                    data["Amount"] = Chuba.crypto_sub_amount * (days / 30)
                await ctx.set("PaymentConfirm")
            else:
                pass

    @button(custom_id=AnyUserButtons.ANY_GOBACK)
    async def go_back(self, ctx: StateContext):
        await ctx.set("UserMenu")
