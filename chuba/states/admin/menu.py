
from yaml import YAMLError

from chuba.bot import Chuba

from chuba.state import (
    button,
    StateContext,
    StateEventType,
    DiscordMessageState,
    DiscordMessageStateForm)
from chuba.buttons import AdminButtons


class AdminMenuForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "AdminMenu")


class AdminMenu(DiscordMessageState):

    form = AdminMenuForm()

    @button(custom_id=AdminButtons.ADMIN_PROMOS)
    async def generate_promos(self, ctx: StateContext) -> None:
        await ctx.set("AdminPromoRole")

    @button(custom_id=AdminButtons.ADMIN_ABOUT_USER)
    async def show_user_info(self, ctx: StateContext) -> None:
        await ctx.set("AdminUserInfoId")

    @button(custom_id=AdminButtons.ADMIN_BECOMES_USER)
    async def show_user_menu(self, ctx: StateContext) -> None:
        await ctx.set("UserOffer")

    @button(custom_id=AdminButtons.ADMIN_UPDATE_CONFIG)
    async def update_config_file(self, ctx: StateContext) -> None:
        try:
            await Chuba.config.reload_async()
        except YAMLError as yaml_error:
            print(yaml_error.args)
        else:
            await ctx.set("AdminMenu")
