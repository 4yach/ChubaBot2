
from chuba.log import log
from chuba.bot import Chuba, ChubaBot
from chuba.utils import ipv4net
from discord.ext.commands import Cog

from chuba.payment.anymoney import AnyMoney, AnyMoneySetup, CallbackModel


class AnyMoneyCog(Cog):

    def __init__(self, bot: ChubaBot, api_key: str, merchant_id: int, callback_url: str):
        self.bot = bot
        self.loop = bot.loop
        self.api_key = api_key
        self.merchant_id = merchant_id
        self.callback_url = callback_url

    async def handle_payment(self, model: CallbackModel):
        if model.status == "done":
            user_id, invoice_id = model.externalid.split("-", 1)
            self.bot.dispatch(
                "payment_received",
                model.in_amount,
                model.in_curr,
                int(user_id),
                invoice_id)

    @Cog.listener()
    async def on_ready(self):
        log.info("Инициализация Any Money")

        am = self.bot.am_client = AnyMoney(self.api_key, self.merchant_id)

        am.callback_url = self.callback_url

        await am.setup_notifier(self.bot.webhook, AnyMoneySetup(
            "/anymoney/pay",
            self.handle_payment
        ))
