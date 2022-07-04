
from discord.ext.commands import Bot, Cog


class PaymentCog(Cog):

    def __init__(self, bot):
        self.bot: Bot = bot

    @Cog.listener()
    async def on_payment_received(self, _amount, _curr, user_id, invoice_id):
        sub, days, code = invoice_id.split('-')

        self.bot.dispatch("subscription_added", user_id, sub, int(days))
