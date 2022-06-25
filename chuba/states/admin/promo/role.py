

from discord import Guild
from discord_components import Select, SelectOption

from chuba.bot import Chuba

from chuba.state import (
    button,
    message,
    StateContext,
    MessageEvent,
    DiscordMessageState,
    DiscordMessageStateForm)

from chuba.selects import AdminSelects
from chuba.buttons import AnyUserButtons

from discord.utils import find


class AdminPromoRoleForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "AdminPromoRole")


class AdminPromoRole(DiscordMessageState):

    form = AdminPromoRoleForm()

    async def setup(self, ctx: StateContext) -> None:
        guild_id: int = Chuba.config.get_value("server_specific", "id")
        guild: Guild = await Chuba.fetch_guild(guild_id)

        select_layout = [Select(
            options=[
                SelectOption(label=r.name, value=r.name) for r in guild.roles
            ],
            custom_id=AdminSelects.ADMIN_PROMO_ROLE,
            placeholder=Chuba.config.get_value("strings", "admin_promo_roles_placeholder")
        )]

        select_layout.extend(self.form.component_layout)

        await self.show(
            ctx,
            embed=self.form.embed,
            components=select_layout
        )

    @message()
    async def select_role(self, ctx: StateContext):
        guild_id: int = Chuba.config.get_value("server_specific", "id")
        guild: Guild = await Chuba.fetch_guild(guild_id)
        event = ctx.event
        if isinstance(event, MessageEvent):
            text = event.message.content
            role = find(lambda r: r.name == text, guild.roles)
            if role:
                with ctx.data() as data:
                    data["Role"] = text
                await ctx.set("AdminPromoAmount")
            else:
                await event.message.reply(content="Такой роли не существует, создайте ее")

    @button(custom_id=AnyUserButtons.ANY_GOBACK)
    async def go_back(self, ctx: StateContext):
        await ctx.set("AdminMenu")
