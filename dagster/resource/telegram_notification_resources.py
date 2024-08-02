from dagster import resource
from utils.base_utils import get_environ
from utils.telegram_notification_utils import TelegramNotification


@resource
def telegram_notification():
    host = get_environ("DB_HOST_BOT")
    port = get_environ("DB_PORT_BOT")
    user = get_environ("DB_USER_BOT")
    database = get_environ("DB_NAME_BOT")
    passwd = get_environ("DB_PASS_BOT")
    connection_str = f'host={host} port={port} dbname={database} user={user} password={passwd}'
    telegram_bot_api_token = get_environ("TELEGRAM_BOT_API_TOKEN")
    return TelegramNotification(telegram_bot_api_token, connection_str)
