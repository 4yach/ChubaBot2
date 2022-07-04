
from discord_components import Button

from chuba.bot import Chuba

from chuba.state import (
    button,
    StateContext,
    DiscordMessageState,
    DiscordMessageStateForm)
from chuba.users import UserModel
from chuba.buttons import AnyUserButtons, UserButtons


class UserMenuProfileForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "UserMenuProfile")


class UserMenuProfileLoadingForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "UserMenuProfileLoading")


class UserMenuProfile(DiscordMessageState):

    """Профиль пользователя

    Именно в этой форме отображается вся информация о пользователе,
    которая зарезервирована в базе данных.

    """

    form = UserMenuProfileForm()
    form_loading = UserMenuProfileLoadingForm()

    async def setup(self, ctx: StateContext) -> None:

        message = await self.show(
            ctx, **self.form_loading.to_send())

        user = ctx.user
        embed = self.form.embed
        layout = self.form.component_layout

        nothing: str = Chuba.config.get_value("strings", "nothing")
        user_model: UserModel = await Chuba.user_db.get_user(user.id)

        # Редактируем эмбед
        embed.description = embed.description.format(
            mention=user.mention,
            user_id=user_model.id,
            promo=user_model.promo or nothing,
            subscription=user_model.subscription or nothing,
            vip_subscription=user_model.vip_subscription or nothing,
            last_payment=user_model.last_payment_id or nothing,
            subscription_id=user_model.subscription_id or nothing
        )
        embed.set_thumbnail(url=str(user.avatar_url))

        # редактируем компоненты
        discard_sub_button = layout[0][1]
        discard_sub_button.disabled = user_model.subscription is None

        discard_vip_button = layout[0][2]
        discard_vip_button.disabled = user_model.vip_subscription is None

        await message.edit(
            embed=embed, components=layout)

    @button(custom_id=AnyUserButtons.ANY_GOBACK)
    async def go_back(self, ctx: StateContext):
        await ctx.set("UserMenu")

    @button(custom_id=UserButtons.USER_DISCARD_SUBSCRIPTION)
    async def discard_subscription(self, ctx: StateContext):
        Chuba.dispatch("subscription_declined", ctx.user.id, "SUB")
        await ctx.set("UserMenuProfile")

    @button(custom_id=UserButtons.USER_DISCARD_VIP)
    async def discard_vip(self, ctx: StateContext):
        Chuba.dispatch("subscription_declined", ctx.user.id, "VIP")
        await ctx.set("UserMenuProfile")

    @button(custom_id=UserButtons.USER_DISCARD_RECURRENT)
    async def discard_recurrent(self, ctx: StateContext):
        user_id = ctx.user.id
        user_model: UserModel = await Chuba.user_db.get_user(user_id)

        Chuba.dispatch(
            "recurrent_declined",
            user_id,
            user_model.subscription_id)

        await ctx.set("UserMenuProfile")
