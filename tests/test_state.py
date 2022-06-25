
from discord import User
from unittest import IsolatedAsyncioTestCase

from chuba.state import event, State, StateMachine, StateContext, StateEventType, StateEvent


_FAKE_USER_DATA = {
    "id": 1,
    "username": "4yach",
    "discriminator": 4444,
    "avatar": None
}

_FAKE_USER_DATA_2 = {
    "id": 2,
    "username": "4yach",
    "discriminator": 4444,
    "avatar": None
}


class TestFakeContext:

    def __init__(self, user: User):
        self.user = user


class TestStateEventType(StateEventType):
    FAKE_MESSAGE = 0


class TestFakeMessageEvent(StateEvent):

    type = TestStateEventType.FAKE_MESSAGE

    def __init__(self, ctx: TestFakeContext):
        self.ctx = ctx
        self.user = ctx.user

    def matches(self, filters):
        return True


class MenuTestState(State):

    @event(TestStateEventType.FAKE_MESSAGE)
    async def handler(self, ctx: StateContext):
        data = await ctx.data()
        data["Checked"] = True


class StateTest(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.fake_user = User(state=None, data=_FAKE_USER_DATA)
        self.fake_user2 = User(state=None, data=_FAKE_USER_DATA_2)
        self.state_machine = StateMachine()

        self.state_machine.register(MenuTestState())

        await self.state_machine.set(self.fake_user, "MenuTestState")
        await self.state_machine.set(self.fake_user2, "MenuTestState")

    def test_register(self):
        """Проверка регистрации новых состояний в таблице состояний
        """
        self.state_machine.register(MenuTestState())
        self.assertIn("MenuTestState", self.state_machine.state_map)

    async def test_set_state(self):
        """Проверка установки состояния для данного пользователя
        """
        self.assertEqual("MenuTestState", self.state_machine.states[self.fake_user.id])

    async def test_data(self):
        _data0 = await self.state_machine.data(self.fake_user)
        _data1 = await self.state_machine.data(self.fake_user2)

        # проверяем указывают ли `_data0` и `_data1` на разные словари
        self.assertIsNot(_data0, _data1)

        _data0["Amount"] = 2000
        _data1["Amount"] = 1000

        _data0_c = await self.state_machine.data(self.fake_user)
        _data1_c = await self.state_machine.data(self.fake_user2)

        self.assertEqual(_data0["Amount"], _data0_c["Amount"])
        self.assertEqual(_data1["Amount"], _data1_c["Amount"])

    async def test_handle_event(self):
        await self.state_machine.handle_event(TestFakeMessageEvent(TestFakeContext(self.fake_user)))
        self.assertEqual((await self.state_machine.data(self.fake_user))["Checked"], True)
