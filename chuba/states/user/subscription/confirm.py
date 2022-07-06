
from chuba.bot import Chuba

from chuba.state import (
    button,
    StateContext,
    DiscordMessageState,
    DiscordMessageStateForm)

from chuba.buttons import UserButtons


class PaymentConfirmForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "PaymentConfirm")


class PaymentConfirm(DiscordMessageState):

    form = PaymentConfirmForm()

    async def setup(self, ctx: StateContext) -> None:
        embed = self.form.embed

        with ctx.data() as data:
            embed.description = embed.description.format(
                amount=data["Amount"], currency=data["Currency"])
            await self.show(
                ctx,
                embed=embed,
                components=self.form.component_layout)

    @button(custom_id=UserButtons.USER_PAYMENT_CONFIRM)
    async def payment_confirm(self, ctx: StateContext):
        with ctx.data() as data:
            currency = data["Currency"]
            match currency:
                case "RUB":
                    await ctx.set("PaymentRecurrent")
                case "USDT":
                    await ctx.set("AnyMoneyView")

    @button(custom_id=UserButtons.USER_PAYMENT_REFUSE)
    async def payment_refuse(self, ctx: StateContext):
        await ctx.set("UserMenu")
