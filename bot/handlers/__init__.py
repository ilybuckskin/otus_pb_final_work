import asyncio
import sys

from aiogram import Router

from . import (add_notifications, basic_commands, dagster_get_runs,
               management_notifications)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(dagster_get_runs.check_session())


def get_routers() -> list[Router]:
    return [
        basic_commands.router,
        add_notifications.router,
        management_notifications.router,
        dagster_get_runs.router,
    ]
