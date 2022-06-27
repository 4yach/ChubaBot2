
from chuba.bot import Chuba

from chuba.users import UserModel

from chuba.state import (
    button,
    StateContext,
    DiscordMessageState,
    DiscordMessageStateForm)
from chuba.buttons import AnyUserButtons, AdminButtons


class AdminUserInfoLoadingForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "AdminUserInfoLoading")


class AdminUserInfoForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "AdminUserInfo")


class AdminUserInfo(DiscordMessageState):

    """Ввод количества промокодов
    """

    form = AdminUserInfoForm()
    form_loading = AdminUserInfoLoadingForm()

    async def setup(self, ctx: StateContext) -> None:
        embed = self.form.embed
        message = await self.show(ctx, **self.form_loading.to_send())

        with ctx.data() as data:
            user_model: UserModel = data["UserModel"]

            embed.description = embed.description.format(
                user_id=user_model.id,
                promo=user_model.promo,
                subscription=user_model.subscription,
                vipsubscription=user_model.vip_subscription)

            await message.edit(
                embed=embed,
                components=self.form.component_layout)

    @button(custom_id=AnyUserButtons.ANY_GOBACK)
    async def go_back(self, ctx: StateContext):
        await ctx.set("AdminMenu")

    @button(custom_id=AdminButtons.ADMIN_GIVE_SUB)
    async def give_sub(self, ctx: StateContext):
        with ctx.data() as data:
            data["Sub"] = "SUB"
        await ctx.set("AdminUserInfoDays")

    @button(custom_id=AdminButtons.ADMIN_GIVE_VIP)
    async def give_vip(self, ctx: StateContext):
        with ctx.data() as data:
            data["Sub"] = "VIP"
        await ctx.set("AdminUserInfoDays")

    @button(custom_id=AdminButtons.ADMIN_DROP_SUB)
    async def drop_sub(self, ctx: StateContext):
        with ctx.data() as data:
            Chuba.dispatch("subscription_declined", "SUB", data["UserId"])
        await ctx.set("AdminUserInfo")

    @button(custom_id=AdminButtons.ADMIN_DROP_VIP)
    async def drop_vip(self, ctx: StateContext):
        with ctx.data() as data:
            Chuba.dispatch("subscription_declined", "VIP", data["UserId"])
        await ctx.set("AdminUserInfo")

    @button(custom_id=AdminButtons.ADMIN_DROP_PROMO)
    async def drop_promo(self, ctx: StateContext):
        with ctx.data() as data:
            Chuba.dispatch("promo_declined", data["UserId"])
        await ctx.set("AdminUserInfo")

    @button(custom_id=AdminButtons.ADMIN_GIVE_PROMO)
    async def give_promo(self, ctx: StateContext):
        await ctx.set("AdminUserPromo")
