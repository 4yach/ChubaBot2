

class PaymentBase:

    endpoint: str

    async def create(self, invoice_id: str, **kwargs) -> dict:
        raise NotImplemented

    async def check(self, invoice_id: str) -> dict:
        raise NotImplemented

    async def cancel(self, invoice_id: str) -> dict:
        raise NotImplemented


class Bill:
    pass
