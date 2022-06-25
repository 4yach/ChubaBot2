
from yaml import load, Loader
from typing import Dict, Any
from asyncio import get_event_loop


class Configuration:

    _raw: Dict = {}

    def __init__(self, fp: str, update_dict: Dict[str, Dict], encoding="utf-8"):
        self._fp = fp
        self._raw = update_dict
        self._encoding = encoding
        self._loop = get_event_loop()

    def __repr__(self):
        return f"Configuration(filename={self._fp})"

    @classmethod
    def load(cls, fp, encoding="utf-8") -> "Configuration":
        """Загружаем конфигурацию из JSON файла

        :param fp: путь к файлу конфигурации
        :param encoding: кодировка, обычно `utf-8`
        :return: Configuration-объект
        """
        with open(fp, 'r', encoding=encoding) as _json:
            return cls(fp, load(_json, Loader), encoding)

    def reload(self):
        with open(self._fp, 'r', encoding=self._encoding) as _json:
            self._raw = load(_json, Loader)

    async def reload_async(self):
        await self._loop.run_in_executor(None, self.reload)

    def get_value(self, category_name: str, value_name: str) -> Any:
        if category_name in self._raw:
            return self._raw[category_name][value_name]
        else:
            raise ValueError("no such category in configuration file")

    def has_value(self, category_name: str, value_name: str) -> Any:
        return category_name in self._raw and value_name in self._raw[category_name]
