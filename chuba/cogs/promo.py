
from os import listdir
from json import JSONDecodeError
from typing import Dict

from os.path import join
from chuba.log import log
from chuba.promo import PromoHolder, PromoStorage

from discord.ext.tasks import loop
from discord.ext.commands import Cog


class PromoCog(Cog):

    promo_storage: PromoStorage

    def __init__(self, bot, promos_directory):
        self._bot = bot
        self._promos_directory = promos_directory

    @Cog.listener()
    async def on_ready(self):
        """Кеширование всех промокодов с диска
        """
        log.info("Инициализация промохолдеров")

        self.promo_storage = self._bot.promo_storage = PromoStorage(self._promos_directory)
        for promo_fn in listdir(self._promos_directory):
            if promo_fn.endswith(".json"):
                try:
                    self.promo_storage.load_promoholder(join(self._promos_directory, promo_fn))
                except JSONDecodeError as _exc:
                    log.error(f"Невожможно открыть промохолдер {promo_fn}, причина: {_exc}")

        self.check_promos_expdate.start()

        log.info(f"Всего закешировано промохолдеров: {len(self.promo_storage.cached_promo_holders)}")

    @loop(hours=24.0)
    async def check_promos_expdate(self):
        """Проверка невалидных промокодов (каждые сутки)
        """

        log.info("Проверка невалидных промокодов (каждые сутки)")

        for _, _promo in self.promo_storage.cached_promo_holders.copy().items():
            _days = _promo.days_remain()

            log.info(f"Обнаружен промокод с ролью {_promo.role}, дней осталось: {_days}")

            # в случаем когда срок годности промокодов истек
            if _days < 0:
                # удаляем базу промокодов
                _promo.delete()
                # удаляем базу из кеша
                self.promo_storage.remove_promo_holder(_promo.name)
