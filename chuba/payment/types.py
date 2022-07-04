
from aiohttp.web import Application


class SetupNotifierContext:
    pass


class PaymentBase:

    endpoint: str

    async def create(self, invoice_id: str, **kwargs):
        raise NotImplemented

    async def cancel(self, invoice_id: str):
        raise NotImplemented

    async def cancel_recurrent(self, subscription_id: str):
        raise NotImplemented

    async def setup_notifier(self, webhook: Application, ctx: SetupNotifierContext):
        pass
