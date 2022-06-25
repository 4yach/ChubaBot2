
from aiocloudpayments import AioCpClient

from chuba.bot import Chuba

from chuba.state import (
    button,
    ButtonEvent,
    StateContext,
    DiscordMessageState,
    DiscordMessageStateForm)

from chuba.buttons import UserButtons


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
                invoice_id=data["InvoiceId"],
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
                "subscription_payed",
                check=lambda s, d, ui: ui == ctx.user.id)

            await message.edit(**self.success_form.to_send())

    @button(custom_id=UserButtons.USER_PAYMENT_CHECK)
    async def check_payment(self, ctx: StateContext):
        event = ctx.event
        with ctx.data() as data:
            payload = await Chuba.am_client.check(data["InvoiceId"])
            if isinstance(event, ButtonEvent):
                status = payload["result"]["status"]
                if status == "done":
                    await event.interaction.respond(
                        content=f"Платеж прошел, данное сообщение можно скрыть")
                    Chuba.dispatch(
                        "subscription_payed",
                        data["Subscription"],
                        data["Days"],
                        ctx.user.id
                    )
                else:
                    await event.interaction.respond(
                        content=f"Платеж еще не прошел, статус {status}. Данное сообщение можно скрыть.")

    @button(custom_id=UserButtons.USER_PAYMENT_CANCEL)
    async def payment_cancel(self, ctx: StateContext):
        await ctx.set("UserMenu")
