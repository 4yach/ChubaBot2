
from chuba.bot import Chuba

from chuba.utils import randseq7

from chuba.state import (
    button,
    StateContext,
    DiscordMessageState,
    DiscordMessageStateForm)

from chuba.buttons import UserButtons, AnyUserButtons


class AnyMoneyWaitingViewForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "AnyMoneyWaitingView")


class AnyMoneyViewForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "AnyMoneyView")


class AnyMoneySuccessViewForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "AnyMoneySuccessView")


class AnyMoneyView(DiscordMessageState):

    form = AnyMoneyViewForm()
    waiting_form = AnyMoneyWaitingViewForm()
    success_form = AnyMoneySuccessViewForm()

    async def setup(self, ctx: StateContext):
        message = await self.show(ctx, **self.waiting_form.to_send())

        with ctx.data() as data:
            # создаем ордер на оплату и получаем его ID для возможности
            # отменить платеж, по нажатию на кнопку
            order = await Chuba.am_client.create(
                invoice_id=f"{ctx.user.id}-{data['Subscription']}-{data['Days']}-{randseq7()}",
                amount=str(data["Amount"]),
                currency=data["Currency"],
                lifetime="1d"
            )

            # отображаем новый эмбед пользователю с готовой для оплаты ссылкой
            embed = self.form.embed
            embed.description = embed.description.format(url=order["result"]["paylink"])
            await message.edit(
                embed=embed,
                components=self.form.component_layout)

            # ждем, когда пользователь оплатит подписку
            await Chuba.wait_for(
                "payment_received",
                check=lambda am, curr, usid, inid: usid == ctx.user.id)

            await message.edit(**self.success_form.to_send())

    @button(custom_id=UserButtons.USER_PAYMENT_CANCEL)
    async def payment_cancel(self, ctx: StateContext):
        await ctx.set("UserMenu")

    @button(custom_id=AnyUserButtons.ANY_GOBACK)
    async def go_back(self, ctx: StateContext):
        await ctx.set("UserMenu")
