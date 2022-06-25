
from typing import List
from discord_components import Button

from chuba.bot import Chuba

from chuba.state import (
    button,
    StateEvent,
    ButtonEvent,
    StateContext,
    DiscordMessageState,
    DiscordMessageStateForm)
from chuba.buttons import UserButtons, AdminButtons


class UserMenuForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "UserMenu")

    @property
    def promo_already_component_layout(self) -> List:
        return self.build_button_layout(self.data.get("promo_already_buttons", []))


class UserMenu(DiscordMessageState):

    form = UserMenuForm()

    @button(custom_id=UserButtons.MENU_PROMO)
    async def apply_promo(self, context: StateContext) -> None:
        await context.set("UserMenuPromo")

    @button(custom_id=UserButtons.MENU_SUBSCRIPTION)
    async def buy_subscription(self, context: StateContext) -> None:
        await context.set("SelectCurrency")

    @button(custom_id=UserButtons.MENU_DISCARD_SUB)
    async def discard_subscription(self, context: StateContext) -> None:
        pass

    @button(custom_id=UserButtons.MENU_PROFILE)
    async def profile(self, context: StateContext) -> None:
        await context.set("UserMenuProfile")

    @button(custom_id=AdminButtons.ADMIN_RETURN)
    async def admin_return(self, context: StateContext) -> None:
        await context.set("AdminMenu")

    async def setup(self, ctx: StateContext) -> None:
        user = ctx.user
        user_id: int = user.id
        layout: list = self.form.component_layout
        menu_promo_button: Button = layout[0][0]
        menu_subscription_button: Button = layout[0][1]

        user_model = await Chuba.user_db.get_user(user_id)
        if user_model.promo:
            menu_promo_button.disabled = True
        else:
            menu_subscription_button.disabled = True

        if user_id in Chuba.config.get_value("server_specific", "admins"):
            layout.append(Button.from_json(Chuba.config.get_value("buttons", "AdminReturnButton")))

        await self.show(
            ctx,
            embed=self.form.embed,
            components=layout
        )
