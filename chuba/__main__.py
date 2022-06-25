
from sys import argv
from discord import Intents
from argparse import ArgumentParser, Namespace

from chuba.log import log
from chuba.bot import Chuba
from chuba.cogs import (
    DevErrorCog,
    ConfigCog,
    StateCog,
    EventCog,
    StartCog,
    PromoCog,
    RolesCog,
    DCSetupCog,
    DatabaseCog,
    WebhookCog,
    AnyMoneyCog,
    CloudPaymentsCog,
    WebhookStarterCog)

_DEFAULT_PROMOS_PATH: str = "chuba_promos/"
_DEFAULT_CONFIG_PATH: str = "chuba.yaml"
_DEFAULT_USERSDB_PATH: str = "chuba_users.db"

arg_parser = ArgumentParser(
    description="ChubaCoint Bot - бот для Дискорд сирвера Глеба Корнилова")

arg_parser.add_argument(
    "-t", "--token",
    dest="token",
    help="Токен Дискорд бота",
    required=True)

arg_parser.add_argument(
    "-c", "--config",
    dest="config",
    help="Путь к файлу конфигурации в формате JSON",
    required=False)

arg_parser.add_argument(
    "-d", "--database",
    dest="database",
    help="Путь к базе данных (Используется SQLite3)",
    required=False)

arg_parser.add_argument(
    "-p", "--promos",
    dest="promos",
    help="Директория с промохолдерами",
    required=False)

arg_parser.add_argument(
    "--cp-pid",
    dest="cp_public_id",
    help="Публичный ID CloudPayments",
    required=False)

arg_parser.add_argument(
    "--cp-as",
    dest="cp_api_secret",
    help="Секретный ключ API",
    required=False)

arg_parser.add_argument(
    "--am-api-key",
    dest="am_api_key",
    help="Ключ API Any.Money",
    required=False)

arg_parser.add_argument(
    "--am-merchant-id",
    dest="am_merchant_id",
    help="Merchant ID Any.Money",
    required=False)

arg_parser.add_argument(
    "--webhook-ip",
    dest="webhook_ip",
    help="IP вебхука",
    required=False,
    default="127.0.0.1")

arg_parser.add_argument(
    "--webhook-port",
    type=int,
    dest="webhook_port",
    help="порт вебхука",
    required=False,
    default=8080)


if __name__ == '__main__':
    namespace: Namespace = arg_parser.parse_args(argv[1:])

    log.info("Стартовал бот ChubaCoin")

    Chuba.add_cog(DevErrorCog(Chuba))

    Chuba.add_cog(DCSetupCog(Chuba))

    Chuba.add_cog(ConfigCog(Chuba, namespace.config or _DEFAULT_CONFIG_PATH))
    Chuba.add_cog(DatabaseCog(Chuba, namespace.database or _DEFAULT_USERSDB_PATH))
    Chuba.add_cog(PromoCog(Chuba, namespace.promos or _DEFAULT_PROMOS_PATH))
    Chuba.add_cog(StateCog(Chuba))

    Chuba.add_cog(StartCog(Chuba))
    Chuba.add_cog(EventCog(Chuba))
    Chuba.add_cog(WebhookCog(Chuba))
    Chuba.add_cog(AnyMoneyCog(Chuba, namespace.am_api_key, namespace.am_merchant_id))
    Chuba.add_cog(CloudPaymentsCog(Chuba, namespace.cp_public_id, namespace.cp_api_secret))
    Chuba.add_cog(RolesCog(Chuba))
    Chuba.add_cog(WebhookStarterCog(Chuba, namespace.webhook_ip, namespace.webhook_port))

    Chuba.run(namespace.token)
