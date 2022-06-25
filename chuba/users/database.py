
from typing import Dict
from aiosqlite import connect, DatabaseError

from chuba.users.model import UserModel
from chuba.users.queries import (
    CREATE_USERS_TABLE,
    CREATE_USER,
    GET_USER,
    UPDATE_USER,
    GET_EXPIRIED_SUBSCRIPTIONS,
    GET_EXPIRIED_VIPSUBSCRIPTIONS)


class UserContext:

    def __init__(self, db: "UsersDatabase", user_id: int):
        self._db = db
        self._user_id = user_id
        self._user_model = None

    async def __aenter__(self) -> UserModel:
        self._user_model = await self._db.get_user(self._user_id)
        return self._user_model

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._db.update_user(self._user_model)


class UsersDatabase:

    cached_users: Dict[int, UserModel]
    """Закешированные пользователи
    
    Чтобы не обращаться к базе данных множество раз, используем кеш
    """

    def __init__(self, db_path: str):
        self._connection = connect(db_path)
        self.db_path = db_path
        self.cached_users = {}

    async def setup(self) -> None:
        """Создание базы данных и таблиц внутри
        """
        async with connect(self.db_path) as _c:
            await _c.execute(CREATE_USERS_TABLE)

    async def create_user(self, user_id: int):
        """Создать запись о пользователе по его ID

        Запись будет создана в базе данных и в кэше

        :param user_id: ID пользователя
        """
        async with connect(self.db_path) as _c:
            await _c.execute(CREATE_USER, (user_id, ))
            await _c.commit()

    def user(self, user_id: int) -> UserContext:
        """Удобный контекстный менеджер

        :param user_id: ID пользователя
        :return: контекстный менеджер
        """
        return UserContext(self, user_id)

    async def get_user(self, user_id: int) -> UserModel | None:
        """Получить запись о пользователе в базе по его ID

        :param user_id: ID пользователя
        :return: модель пользователя `UserModel`, если существует, иначе None
        :rtype: UserModel
        """
        if user_id in self.cached_users:
            return self.cached_users[user_id]
        else:
            async with connect(self.db_path) as _c:
                async with _c.execute(GET_USER, (user_id, )) as _cursor:
                    _u = UserModel.from_sql(await _cursor.fetchone())
                    if _u:
                        self.cached_users[user_id] = _u
                    return _u

    async def update_user(self, user_model: UserModel) -> None:
        """Обновить данные о пользователе в базе данных по его модели

        :param user_model: модель пользователя
        """
        async with connect(self.db_path) as _c:
            await _c.execute(UPDATE_USER, (*user_model.to_sql(), user_model.id))
            await _c.commit()

    async def try_register_promo(self, promo: str, user_id: int) -> bool:
        """Попытаться зарегистрировать промокод для пользователя

        :param promo: промокод
        :param user_id: ID пользователя, для которого нужно попытаться зарегистрировать промокод
        :return: True при успешной регистрации (если ранее такой промокод не встречался), иначе False
        """
        try:
            async with self.user(user_id) as user_model:
                user_model.promo = promo
            return True
        except DatabaseError:
            return False

    async def get_expiried_subscriptions(self):
        async with connect(self.db_path) as _c:
            async with _c.execute(GET_EXPIRIED_SUBSCRIPTIONS) as _cursor:
                return await _cursor.fetchall()

    async def get_expiried_vipsubscriptions(self):
        async with connect(self.db_path) as _c:
            async with _c.execute(GET_EXPIRIED_VIPSUBSCRIPTIONS) as _cursor:
                return await _cursor.fetchall()
