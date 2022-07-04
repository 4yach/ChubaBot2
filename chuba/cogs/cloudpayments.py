
from chuba.log import log
from chuba.bot import ChubaBot
from chuba.utils import ipv4net
from chuba.payment.cloudpayments import CloudPayments, CloudPaymentsSetup

from aiocloudpayments import Result
from aiocloudpayments.types.notifications import PayNotification, CheckNotification

from discord.ext.commands import Cog


_IP_WHITELIST = {
    "130.193.70.192",
    "185.98.85.109",
    *ipv4net("91.142.84.0/27"),
    *ipv4net("185.98.81.0/28"),
    *ipv4net("87.251.91.160/27"),
}


class CloudPaymentsCog(Cog):

    cp_client: CloudPayments

    def __init__(self, bot: ChubaBot, public_id: str, api_secret: str):
        self.bot = bot
        self.loop = bot.loop
        self.public_id = public_id
        self.api_secret = api_secret

    async def check(self, notification: CheckNotification):
        values = notification.invoice_id.split("-")
        if len(values) != 3:
            return Result.WRONG_ORDER_NUMBER

    async def pay(self, notification: PayNotification):
        user_id = int(notification.account_id)

        self.bot.dispatch(
            "payment_received",
            int(notification.amount),
            notification.currency,
            user_id,
            notification.invoice_id)

        sub_id = notification.subscription_id
        if sub_id:
            self.bot.dispatch("recurrent_applied", user_id, sub_id)

        return Result.OK

    @Cog.listener()
    async def on_recurrent_declined(self, _user_id: int, sub_id: str):
        await self.cp_client.cancel_recurrent(sub_id)

    @Cog.listener()
    async def on_ready(self):
        log.info("Инициализация обработчика событий CloudPayments")

        self.cp_client = self.bot.cp_client = CloudPayments(self.public_id, self.api_secret)

        await self.cp_client.setup_notifier(
            self.bot.webhook,
            CloudPaymentsSetup(
                "/cloudpayments",
                pay=self.pay,
                pay_path="/pay",
                check=self.check,
                check_path="/check",
                check_hmac=True,
                ip_whitelist=_IP_WHITELIST
            )
        )
