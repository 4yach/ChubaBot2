
from typing import Callable
from dataclasses import dataclass

from chuba.payment.types import PaymentBase, SetupNotifierContext
from chuba.payment.endpoints import Endpoints

from aiohttp.web import Application, Request, Response, json_response

from aiocloudpayments import AioCpClient, AiohttpDispatcher, Result, Router
from aiocloudpayments.types import Order
from aiocloudpayments.utils.hmac_check import hmac_check
from aiocloudpayments.dispatcher.aiohttp_dispatcher import NOTIFICATION_TYPES


class _CloudPaymentsFixedDispatcher(AiohttpDispatcher):

    async def process_request(self, request: Request) -> Response:
        if self.ip_whitelist and request.remote not in self.ip_whitelist and "0.0.0.0" not in self.ip_whitelist:
            return json_response(status=401)
        if self.check_hmac is True and hmac_check(
                await request.read(),
                self.cp_client._api_secret,  # noqa
                request.headers.get("Content-HMAC")) is False:
            return json_response(status=401)
        name = self._web_paths[request.url.name]
        notification_type = NOTIFICATION_TYPES.get(name)
        if notification_type is None:
            return json_response(status=500)
        notification = notification_type(**(await request.post()))
        result = await self.process_notification(notification)
        if result == Result.INTERNAL_ERROR:
            return json_response(status=500)
        if result:
            return json_response({"code": result.value})


@dataclass
class CloudPaymentsSetup(SetupNotifierContext):

    path: str

    pay: Callable = None
    check: Callable = None

    pay_path: str = None
    check_path: str = None

    check_hmac: bool = True
    ip_whitelist: set = None

    @property
    def router(self) -> Router:
        _router = Router()
        _router.pay.register(self.pay)
        _router.check.register(self.check)
        return _router

    @property
    def dispatcher(self) -> _CloudPaymentsFixedDispatcher:
        _dispatcher = _CloudPaymentsFixedDispatcher()
        _dispatcher.check_hmac = self.check_hmac
        _dispatcher.ip_whitelist = self.ip_whitelist
        return _dispatcher


class CloudPayments(PaymentBase):

    endpoint = Endpoints.CLOUD_PAYMENTS

    def __init__(self, public_id: str, api_secret: str):
        self._cp_client = AioCpClient(public_id, api_secret, base_url=self.endpoint)

    async def create(self, invoice_id: str, **kwargs) -> Order:
        return await self._cp_client.create_order(invoice_id=invoice_id, **kwargs)

    async def cancel(self, invoice_id: str):
        return await self._cp_client.cancel_order(id=invoice_id)

    async def cancel_recurrent(self, subscription_id: str):
        return await self._cp_client.cancel_subscription(subscription_id)

    async def setup_notifier(self, webhook: Application, ctx: CloudPaymentsSetup):
        dispatcher = ctx.dispatcher
        dispatcher.cp_client = self._cp_client
        dispatcher.include_router(ctx.router)
        dispatcher.register_app(
            webhook,
            path=ctx.path, pay_path=ctx.pay_path, check_path=ctx.check_path)
