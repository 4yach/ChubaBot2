# TODO: написать собственный обработчик уведомлений

from aiocloudpayments import AioCpClient, AiohttpDispatcher, Router, Result
from aiocloudpayments.types.notifications import PayNotification

from aiohttp.web import Request, Response, json_response

from chuba.log import log
from chuba.bot import Chuba, ChubaBot
from chuba.utils import ipv4net
from discord.ext.commands import Cog


basic_router = Router()


class FixedAiohttpDispatcher(AiohttpDispatcher):

    async def process_request(self, request: Request) -> Response:
        await super().process_request(request)
        return json_response({"code": 0})


basic_dispathcer = FixedAiohttpDispatcher()


class CloudPaymentsCog(Cog):

    cp_client: AioCpClient

    def __init__(self, bot: ChubaBot, public_id: str, api_secret: str):
        self.bot = bot
        self.loop = bot.loop
        self.public_id = public_id
        self.api_secret = api_secret

    async def pay(self, notification: PayNotification):
        sub, days, _ = notification.invoice_id.split("-")

        self.bot.dispatch(
            "subscription_payed",
            sub,
            int(days),
            int(notification.account_id))

        return Result.OK

    @Cog.listener()
    async def on_ready(self):
        log.info("Инициализация обработчика событий CloudPayments")

        cp = self.bot.cp_client = AioCpClient(self.public_id, self.api_secret)

        basic_dispathcer.cp_client = cp
        basic_dispathcer.check_hmac = True
        basic_dispathcer.ip_whitelist = {
            "130.193.70.192",
            "185.98.85.109",
            *ipv4net("91.142.84.0/27"),
            *ipv4net("185.98.81.0/28"),
            *ipv4net("87.251.91.160/27"),
        }

        basic_router.pay.register(self.pay)
        basic_dispathcer.include_router(basic_router)
        basic_dispathcer.register_app(
            self.bot.webhook,
            path="/cloudpayments",
            pay_path="/pay")
