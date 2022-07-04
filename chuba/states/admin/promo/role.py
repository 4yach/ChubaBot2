

from discord import Guild

from chuba.bot import Chuba

from chuba.state import (
    button,
    message,
    StateContext,
    MessageEvent,
    DiscordMessageState,
    DiscordMessageStateForm)

from chuba.buttons import AnyUserButtons

from discord.utils import find


class AdminPromoRoleForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "AdminPromoRole")


class AdminPromoRole(DiscordMessageState):

    form = AdminPromoRoleForm()

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
