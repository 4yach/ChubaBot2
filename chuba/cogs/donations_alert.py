
from discord import User, Embed, TextChannel

from chuba.bot import Chuba

from discord.ext.commands import Bot, Cog


class DonationsAlertCog(Cog):

    def __init__(self, bot):
        self.bot: Bot = bot

    @Cog.listener()
    async def on_payment_received(self, amount, curr, user_id, invoice_id):

        if "VIP" in invoice_id:
            embed: Embed = Embed.from_dict(
                Chuba.config.get_value("embed", "DonationEmbed"))

            channel: TextChannel = await self.bot.fetch_channel(
                Chuba.config.get_value("server_specific", "donations_alert_channel"))

            embed.description = embed.description.format(
                amount=amount,
                mention=f"<@{user_id}>",
                currency=curr)

            await channel.send(embed=embed)
