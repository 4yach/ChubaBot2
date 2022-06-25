

from discord import Guild
from discord_components import Select, SelectOption

from chuba.bot import Chuba

from chuba.state import (
    button,
    select,
    StateContext,
    SelectEvent,
    DiscordMessageState,
    DiscordMessageStateForm)

from chuba.selects import AdminSelects
from chuba.buttons import AnyUserButtons


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

    @select(custom_id=AdminSelects.ADMIN_PROMO_ROLE)
    async def select_role(self, ctx: StateContext):
        event = ctx.event
        if isinstance(event, SelectEvent):
            with ctx.data() as data:
                data["Role"] = event.interaction.values[0]
            await ctx.set("AdminPromoAmount")

    @button(custom_id=AnyUserButtons.ANY_GOBACK)
    async def go_back(self, ctx: StateContext):
        await ctx.set("AdminMenu")
