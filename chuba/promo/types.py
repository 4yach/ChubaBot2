
from typing import Dict

from os import remove
from json import load, dump
from random import sample
from string import ascii_uppercase
from pathlib import Path
from zipfile import ZipFile
from datetime import date

from os.path import join, exists

from chuba.utils import from_iso_8601, randseq7


class PromoHolder:

    role_id: str
    expdate: date
    cached_promos: list

    def __init__(self, fp: str, **kwargs):
        self.fp = fp
        self.name = Path(fp).stem
        self.role = kwargs.pop("role", "")
        self.expdate_raw = kwargs.pop("expdate", None)
        self.expdate = from_iso_8601(self.expdate_raw)
        self.cached_promos = kwargs.pop("promos", [])

    @classmethod
    def promo_generator(cls, index: int):
        return ''.join(sample(ascii_uppercase + str(index), 7))

    @classmethod
    def generate(
            cls,
            path: str,
            role: str,
            expdate: str,
            amount: int) -> "PromoHolder":
        """Сегенрировать промокоды

        Генерация N-го количества промокодов и последующего
        сохранения в память + сохранения в файл

        :param int path: Директория, в которой будут создан файл промокодов
        :param str role: Роль, которую присваивают промокоды
        :param str expdate: Дата в строковом формате DD.MM.YYYY
        (Можно указать время через пробел, например: 17.02.2003 06:14), до которой валиден промокод
        :param int amount: Количество промокодов
        :param function prepr: Функция, генерирующая случайные имена для промокодов, в качестве
        стандратного занчения установлена функция, задающая имена в следующеем ключе: 7 случайно сгенерированных букв
        латинского алфавита

        :return: PromoHolder-объект

        """
        _fp = join(path, randseq7() + ".json")
        return PromoHolder(
            _fp,
            role=role,
            expdate=expdate,
            promos=[cls.promo_generator(i) for i in range(amount)]
        )

    @classmethod
    def fromjson(cls, fp: str) -> "PromoHolder":
        """Загрузить промокоды

        Загрузить JSON файл с промокодами асинхронно и закешировать
        N количество промокодов.

        :param str fp: Путь к файлу
        :return: PromoHolder-объект
        """
        with open(fp, 'r', encoding="utf8") as _fs:
            _source = load(_fs)
            return cls(
                fp,
                role=_source.get("role", ""),
                expdate=_source.get("expdate", ""),
                promos=_source.get("promos", [])
            )

    def days_remain(self) -> int:
        """Количество дней до конца действия промокодов

        Проверяем сколько дней осталось до истечения срока
        годности промокода

        :return int: Количество дней до истечения срока действия
        """
        return (self.expdate - date.today()).days

    def has(self, promo_s: str) -> bool:
        """Имеет ли промохолдер данный промокод

        :param promo_s: промокод
        :return: True, если промохолдер имеет такой промокод, иначе False
        """
        return promo_s in self.cached_promos

    def save(self, ) -> None:
        """Сохранить промохолдер в JSON файл
        """
        with open(self.fp, 'w') as _fs:
            dump({
                "role": self.role,
                "expdate": str(self.expdate),
                "promos": self.cached_promos
            }, _fs)

    def delete(self):
        """Удалить файл промохолдера и ZIP-файл промохолдера, если есть

        :return:
        """
        for file in (self.fp, self.fp + ".zip"):
            if exists(file):
                remove(file)

    def as_zip(self) -> str:
        """Записать промокоды в ZIP-файл

        :return: путь к ZIP-файлу
        """
        _path = self.fp + ".zip"
        _txtname = randseq7() + ".txt"
        with ZipFile(_path, 'w') as _zip:
            with _zip.open(join("promo", _txtname), 'w') as _fs:
                _to_write = ""
                for promo in self.cached_promos:
                    _to_write += "%s;%s\n" % (promo, str(self.expdate))
                _fs.write(_to_write.encode("utf8"))
        return _path


class PromoStorage:

    cached_promo_holders: Dict[str, PromoHolder] = {}

    def __init__(self, promo_path: str):
        self._promo_path = promo_path

    def add_promo_holder(self, promo: PromoHolder) -> None:
        """Добавить промохолдер

        Добавляем промохолдер в словарь промохолдеров по ключу имени его JSON файла

        :param promo: объект промохолдера
        """
        self.cached_promo_holders[promo.name] = promo

    def get_promo_holder(self, promo_name: str) -> PromoHolder:
        """Получить промохолдер по его наименованию

        :param promo_name: наименование промохолдера
        :return: объект промохолдера
        """
        return self.cached_promo_holders.get(promo_name)

    def remove_promo_holder(self, promo_name: str) -> None:
        """Удалить промохолдер по его наименованию

        :param promo_name: наименование промохолдера
        """
        promo_holder = self.cached_promo_holders.pop(promo_name)
        promo_holder.delete()

    def find_containing_promo_holder(self, promo: str) -> PromoHolder:
        """Найти самый первый промохолдер, который содержит данный промокод

        :param promo: промокод для поиска
        :return: объект промохолдера
        """
        for _, _promo in self.cached_promo_holders.items():
            if _promo.has(promo):
                return _promo

    def load_promoholder(self, promo_holder_path: str):
        self.add_promo_holder(PromoHolder.fromjson(promo_holder_path))

    def create_promoholder(self, role: str, expdate: str, amount: int) -> PromoHolder:
        _promo_holder = PromoHolder.generate(self._promo_path, role, expdate, amount)
        self.add_promo_holder(_promo_holder)
        _promo_holder.save()
        return _promo_holder
