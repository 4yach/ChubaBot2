
from typing import Iterable

from time import time
from random import sample
from string import ascii_uppercase
from datetime import date
from ipaddress import IPv4Network


def utcnow_ms() -> int:
    """UTC (Точное координатное) Время в миллискенудах

    :return: время в числовом представлении
    """
    return int(1000 * time())


def to_iso_8601(date_: date):
    return date_.strftime("%Y-%m-%d")


def from_iso_8601(date_string):
    return date.fromisoformat(date_string)


def randseq7() -> str:
    """Генератор 7-буквенной строки

    Простейший генератор строк, состоящих из семи букв,
    в основном используется для наименования файлов, содержащих
    промокоды, и исползуется для создания уникальных платежных ссылок.

    >>> randseq7()
    AQIBKDC

    :return: строка, состоящая из семи случайно подобранных заглавных букв
    """
    return ''.join(sample(ascii_uppercase, 7))


def ipv4net(ipnet: str) -> Iterable[str]:
    return map(str, IPv4Network(ipnet))
