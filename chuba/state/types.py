
from typing import Any, Dict, List, Callable
from discord import Member, User

from chuba.state.event import StateEvent, StateEventType


def event(event_type: StateEventType, **filters):
    """Вспомогательная функция для регистрации функций-обработчиков для состояний

    :param event_type:
    :param filters:
    :return:
    """
    def _wrapper(handler):
        return StateEventHandler(handler, event_type, **filters)
    return _wrapper


class UserDataContext:

    def __init__(self, data):
        self._data = data

    def __enter__(self):
        return self._data

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class StateContext:
    """Контекст состояния

    Используется для уменьшения количества параметров у метод обработчика и т.д.
    Также позволяет вызывать некоторые методы в более короткой форме, ака шорткат (Например метод `set`, который
    задает состояние пользователю).
    """

    user: User | Member
    """Ссылка на пользователя, который вызвал событие
    """

    event: StateEvent
    """Ссылка на событите
    """

    state_machine: "StateMachine"
    """Ссылка на машину состояний
    """

    def __init__(self, user_event: StateEvent, state_machine: "StateMachine"):
        self.user = user_event.user
        self.event = user_event
        self.state_machine = state_machine

    async def set(self, state_name) -> None:
        """Шорткат для метода `StateMachine.set`

        Задает состояние пользователю в машине состояний

        :param state_name: наименование состояния
        """
        await self.state_machine.set(self.event.user, state_name, prev_event=self.event)

    def data(self) -> UserDataContext:
        """Шорткат для метода `StateMachine.data`

        Получеть ссылку на выделенную память

        :return: ссылка на выделенную память
        """
        return self.state_machine.data(self.event.user)

    async def send(self, *args, **kwargs) -> None:
        """Шорткат для метода `Member.send`

        Отправить пользователю сообщение
        """
        await self.event.user.send(*args, **kwargs)


class StateMachine:

    states: Dict[int, str] = {}
    """Текущие состояния пользователей
    
    Состояния пользователей, записанные в виде словаря, где ключ - Discord ID пользователя, значение -
    ID состояния.
    """

    storage: Dict[int, Dict[Any, Any]] = {}
    """Хранилище для данных, которые создаются состояниями
    
    TODO: Данный метод позволяет хранить данные только в оперативной памяти, предполагается разработать интерфейс для
    возможности добавления других типов хранилищ.
    """

    state_map: Dict[str, "State"] = {}
    """Таблица уже инициализированных состояний
    
    Словарь, в котором хранятся зарегистрированные состояния, где ключ - ID состояния, значение - объект состояния
    :ref:`chuba.state.State`.

    Именно, благодаря этой таблице, машина состояний находит подходящий объект состояния для данного пользователя. При
    таком подходе не нужно присваивать объект состояния пользователю в таблице `states`.
    """

    @classmethod
    def register(cls, state: "State") -> None:
        """Зарегистрировать новое состояние в таблице состояний

        :param state: Объект состояния
        """
        cls.state_map[state.__class__.__name__] = state

    async def set(self, user: Member | User, state_name: str, prev_event: StateEvent = None) -> None:
        """Задать новое состояние для пользователя по его ID

        Изменить (Задать) состояние пользователю в таблице и вызвать метод `setup` (корутина) у конкретного состояния

        :param user: пользователь
        :param state_name: наименование состояния
        :param prev_event: ссылка на предыдущее зафиксированное событие (Опционально, обычно None)
        """
        self.states[user.id] = state_name
        if not prev_event:
            prev_event = StateEvent()
            prev_event.user = user
        await self.state_map[state_name].setup(StateContext(prev_event, self))

    def data(self, user: Member | User) -> UserDataContext:
        """Получить ссылку на выделенную для состояния конкретного пользователя память

        :param user: пользователь, для состояния которого выделена память
        """
        _storage = self.storage.get(user.id)
        if not _storage:
            _storage = self.storage[user.id] = {}
        return UserDataContext(_storage)

    async def handle_event(self, event: StateEvent) -> None:
        """Обработчик входящих событий

        Получение входящего события и передача его подходящему состоянию

        :param event: объект события
        """
        _state_name: str = self.states.get(event.user.id)
        if _state_name:
            await self.state_map[_state_name].handle(StateContext(event, self))


class StateEventHandler:
    """Обработчик событий состояния
    """

    def __init__(self, func: Callable, event_type: StateEventType, **filters):
        self._func = func
        self._event_type = event_type
        self._filters = filters

    def __repr__(self):
        return f"Handler(on={self._event_type}, filters={self._filters})"

    async def __call__(self, state: "State", context: StateContext):
        await self._func(state, context)

    def match_type(self, state_event: StateEvent) -> bool:
        """Проверка сходимости типа события обработчика и типа полученного от пользователя события

        :param state_event: объект события
        :return: True, если типы событий равны, иначе False
        """
        return self._event_type == state_event.type and state_event.matches(self._filters)


class State:
    """Состояние, которое может иметь пользователь
    """

    handlers: List[StateEventHandler]

    def __init__(self):
        self.handlers = []
        self._load_handlers()

    def _load_handlers(self):
        for name in dir(self):
            _value = getattr(self, name)
            if isinstance(_value, StateEventHandler):
                self.register(_value)

    def register(self, handler: StateEventHandler) -> None:
        """Зарегистрировать обработчик событий для данного состояния

        Рекомендуется использовать вспомогательный декоратор `event` для обертки методов
        ваших состояний в объект `StateEventHandler`.

        :param handler: объект обработчика событий
        """
        self.handlers.append(handler)

    def unregister(self, handler: StateEventHandler) -> None:
        """Удалить обработчик событий

        :param handler: обработчик для удаления
        :raises ValueError: если обработчик не найден
        """
        self.handlers.remove(handler)

    async def setup(self, ctx: StateContext) -> None:
        """Состояние задано

        Данный метод, вызывается, когда мы задаем состояние при помощи метода `StateMachine.set`

        :param ctx: Контекст состояния
        """

    async def handle(self, context: StateContext) -> None:
        """Обработка полученного от пользователя состояния

        :param context: Контекст состояния
        """
        _event = context.event
        for handler in self.handlers:
            if handler.match_type(_event):
                await handler(self, context)
