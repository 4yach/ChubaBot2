
from discord import File
from datetime import date, timedelta

from chuba.bot import Chuba

from chuba.utils import to_iso_8601

from chuba.state import (
    button,
    StateContext,
    DiscordMessageState,
    DiscordMessageStateForm)

from chuba.buttons import AnyUserButtons


class AdminPromoCreateForm(DiscordMessageStateForm):

    @property
    def data(self) -> dict:
        return Chuba.config.get_value("forms", "AdminPromoCreate")


class AdminPromoCreate(DiscordMessageState):

    """Подтверждение создания промокодов
    """

    form = AdminPromoCreateForm()

    async def setup(self, ctx: StateContext) -> None:

        with ctx.data() as data:
            date_obj = date.today() + timedelta(days=data["Days"])

            promo_holder = Chuba.promo_storage.create_promoholder(
                data["Role"],
                to_iso_8601(date_obj),
                data["Amount"])

            await self.show(
                ctx,
                embed=self.form.embed,
                file=File(promo_holder.as_zip(), spoiler=True),
                components=self.form.component_layout
            )

    @button(custom_id=AnyUserButtons.ANY_GOBACK)
    async def go_back(self, ctx: StateContext):
        await ctx.set("AdminMenu")
