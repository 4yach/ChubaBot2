
from chuba.log import log
from chuba.bot import ChubaBot
from chuba.state import StateMachine, DiscordMessageStateForm

from discord.ext.commands import Bot, Cog

from chuba.states.any import AnyStart
from chuba.states.user import (
    UserMenu,
    UserOffer,
    UserOfferDeclined,
    UserMenuProfile,
    UserMenuPromo,
    UserPromoFailed,
    UserPromoSuccess,

    SelectCurrency,
    SelectSubscription,
    SelectSubscriptionPlan,
    InputVipAmount,
    PaymentConfirm,
    PaymentRecurrent,

    AnyMoneyView,
    CloudPaymentsView
)
from chuba.states.admin import (
    AdminMenu,

    AdminPromoRole,
    AdminPromoAmount,
    AdminPromoDays,
    AdminPromoConfirm,
    AdminPromoCreate,

    AdminUserInfo,
    AdminUserInfoId,
    AdminUserUnknown,
    AdminUserInfoDays,
    AdminUserPromoRole,
    AdminUserPromo
)


class StateCog(Cog):

    _states: tuple = (
        AnyStart(),

        AdminMenu(),
        AdminPromoRole(),
        AdminPromoAmount(),
        AdminPromoDays(),
        AdminPromoConfirm(),
        AdminPromoCreate(),
        AdminUserInfo(),
        AdminUserInfoId(),
        AdminUserUnknown(),
        AdminUserInfoDays(),
        AdminUserPromoRole(),
        AdminUserPromo(),

        UserMenu(),
        UserOffer(),
        UserOfferDeclined(),
        UserMenuProfile(),
        UserMenuPromo(),
        UserPromoFailed(),
        UserPromoSuccess(),

        SelectCurrency(),
        SelectSubscription(),
        SelectSubscriptionPlan(),
        InputVipAmount(),
        PaymentConfirm(),
        PaymentRecurrent(),

        AnyMoneyView(),
        CloudPaymentsView()
    )

    def __init__(self, bot: ChubaBot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        log.info("Инициализация Машины состояний и загрузка состояний")

        state_machine = self.bot.state_machine = StateMachine()

        for state in self._states:
            state_machine.register(state)
