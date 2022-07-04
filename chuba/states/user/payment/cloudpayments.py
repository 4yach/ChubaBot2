
from chuba.bot import Chuba

from chuba.utils import randseq7

from chuba.state import (
    button,
    MessageEvent,
    ButtonEvent,
    StateContext,
    DiscordMessageState,
    DiscordMessageStateForm)

from chuba.buttons import AnyUserButtons, UserButtons


class CloudPaymentsWaitingViewForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "CloudPaymentsWaitingView")


class CloudPaymentsViewForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "CloudPaymentsView")


class CloudPaymentsSuccessViewForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "CloudPaymentsSuccessView")


class CloudPaymentsView(DiscordMessageState):

    form = CloudPaymentsViewForm()
    success_form = CloudPaymentsSuccessViewForm()
    waiting_form = CloudPaymentsWaitingViewForm()

    async def setup(self, ctx: StateContext):
        message = await self.show(ctx, **self.waiting_form.to_send())

        with ctx.data() as data:
            # создаем ордер на оплату и получаем его ID для возможности
            # отменить платеж, по нажатию на кнопку
            order = await Chuba.cp_client.create(
                invoice_id=f"{data['Subscription']}-{data['Days']}-{randseq7()}",
                amount=data["Amount"],
                currency=data["Currency"],
                send_sms=False,
                send_email=False,
                send_viber=False,
                account_id=ctx.user.id,
                description="Оплата подписки",
                require_confirmation=False,
                success_redirect_url=message.jump_url,
                subscription_behavior=data.get("Reccurent")
            )
            data["OrderId"] = order.id

            # отображаем новый эмбед пользователю с готовой для оплаты ссылкой
            embed = self.form.embed
            embed.description = embed.description.format(url=order.url)
            await message.edit(
                embed=embed,
                components=self.form.component_layout)

            # ждем, когда пользователь оплатит подписку
            await Chuba.wait_for(
                "payment_received",
                check=lambda am, curr, usid, inid: usid == ctx.user.id)

            await message.edit(**self.success_form.to_send())

    @button(custom_id=AnyUserButtons.ANY_GOBACK)
    async def go_menu(self, ctx: StateContext):
        await ctx.set("UserMenu")

    @button(custom_id=UserButtons.USER_PAYMENT_CANCEL)
    async def payment_cancel(self, ctx: StateContext):
        with ctx.data() as data:
            await Chuba.cp_client.cancel(invoice_id=data["OrderId"])
        await ctx.set("UserMenu")
