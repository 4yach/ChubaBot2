# TODO: избавиться от дублирования кода

from discord import Guild
from discord.utils import find

from chuba.log import log
from chuba.bot import ChubaBot

from discord.ext.commands import Cog


class RolesCog(Cog):

    def __init__(self, bot: ChubaBot):
        self.bot: ChubaBot = bot

    @Cog.listener()
    async def on_promo_received(self, _promo: str, role_name: str, user_id: int):
        guild_id: int = self.bot.config.get_value("server_specific", "id")

        guild: Guild = await self.bot.fetch_guild(guild_id)
        member = await guild.fetch_member(user_id)

        role = find(lambda r: r.name == role_name, guild.roles)
        if role:
            await member.add_roles(role)
            log.info(f"Выдана роль {role.name} пользвателю {user_id} ({member.display_name})")

    @Cog.listener()
    async def on_subscription_payed(self, sub: str, _days: int, user_id: int, _amount: float, _currency: str):
        guild_id: int = self.bot.config.get_value("server_specific", "id")
        received_role_data: dict = self.bot.config.get_value("subscriptions", sub)
        received_role_id: int = received_role_data["role"]

        guild: Guild = await self.bot.fetch_guild(guild_id)
        member = await guild.fetch_member(user_id)

        role = find(lambda r: r.id == received_role_id, guild.roles)
        if role:
            await member.add_roles(role)
            log.info(f"Выдана роль {role.name} пользвателю {user_id} ({member.display_name})")

    @Cog.listener()
    async def on_subscription_declined(self, sub: str, user_id: int):
        guild_id: int = self.bot.config.get_value("server_specific", "id")
        received_role_data: dict = self.bot.config.get_value("subscriptions", sub)
        received_role_id: int = received_role_data["role"]

        guild: Guild = await self.bot.fetch_guild(guild_id)
        member = await guild.fetch_member(user_id)

        role = find(lambda r: r.id == received_role_id, guild.roles)
        if role:
            await member.remove_roles(role)
            log.info(f"Убрана роль {role.name} пользвателю {user_id} ({member.display_name})")
