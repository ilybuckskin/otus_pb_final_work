import asyncio
import json
import logging
import sys

import psycopg
from aiogram import Bot, Dispatcher, types
from aiogram.utils import exceptions, executor
from utils.base_utils import render_query_with_jinja

from dagster import get_dagster_logger

my_logger = get_dagster_logger()

get_user_by_type = """select distinct telegram_id
from bot_user
inner join public.user_notifications un on bot_user.telegram_id = un.bot_user_id
inner join public.notifications n on n.notification_id = un.notification_id
where notification_name = '{{ notification_name }}';"""


class TelegramNotification:
    def __init__(self, api_token, connection_str):
        self._api_token = api_token
        self._conn = connection_str
        logging.basicConfig(level=logging.INFO)
        self._log = logging.getLogger("dagster")

        self._bot = Bot(token=self._api_token)
        self._dp = Dispatcher(self._bot)

    def get_bot_user(self, notification_name: str):
        rendered_query = render_query_with_jinja(
            get_user_by_type, {"notification_name": notification_name}
        )

        with psycopg.connect(self._conn) as con:
            with con.cursor() as cur:
                cur.execute(rendered_query)
                return [r[0] for r in cur.fetchall()]

    async def _send_message(
        self, user, text: str, disable_notification: bool = False
    ) -> bool:
        try:
            await self._bot.send_message(
                user, text, disable_notification=disable_notification
            )
        except exceptions.BotBlocked:
            self._log.error(f"Target [ID:{user}]: blocked by user")
        except exceptions.ChatNotFound:
            self._log.error(f"Target [ID:{user}]: invalid user ID")
        except exceptions.RetryAfter as e:
            self._log.error(
                f"Target [ID:{user}]: Flood limit is exceeded. Sleep {e.timeout} seconds."
            )
            await asyncio.sleep(e.timeout)
            return await self._send_message(user, text)  # Recursive call
        except exceptions.UserDeactivated:
            self._log.error(f"Target [ID:{user}]: user is deactivated")
        except exceptions.TelegramAPIError:
            self._log.exception(f"Target [ID:{user}]: failed")
        else:
            self._log.info(f"Target [ID:{user}]: success")
            return True
        return False

    def send_message(self, text: str, notification_name: str):
        list_user = self.get_bot_user(notification_name)
        if list_user:
            for user in list_user:
                executor.start(self._dp, self._send_message(user, text))


if __name__ == "__main__":
    telegram_bot_api_token = "7288723112:AAE2tIlrJs1LshdS5a1tuc4fGtwhXQzoYps"
    connection_str = "host=127.0.0.1 dbname=postgres user=postgres password=postgres"
    t = "test error message"
    tg = TelegramNotification(telegram_bot_api_token, connection_str)
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    tg.send_message(str(t), "error")
