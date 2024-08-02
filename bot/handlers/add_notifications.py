from collections import defaultdict
from contextlib import suppress
from typing import Optional

from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from db.requests import add_notifications, get_all_notifications
from sqlalchemy.ext.asyncio import AsyncSession

router = Router(name="Add Notification Router")

user_data = {}


class NotificationCallbackFactory(CallbackData, prefix="notification"):
    action: str
    value: Optional[int] = None
    description: Optional[str] = None


async def get_keyboard_fab(session: AsyncSession):
    notifications = await get_all_notifications(session)
    builder = InlineKeyboardBuilder()
    for i in notifications:
        builder.button(
            text=str(i.notification_name),
            callback_data=NotificationCallbackFactory(
                action="change",
                value=i.notification_id,
                description=i.notification_name,
            ),
        )
    builder.button(
        text="✅ Подтвердить",
        callback_data=NotificationCallbackFactory(action="finish"),
    )
    builder.adjust(1)
    return builder.as_markup()


def del_or_add(user_value: dict, value: int, description: str):
    if value in user_value.keys():
        user_value.pop(value)
    else:
        user_value[value] = description
    return user_value


async def update_notification_text_fab(
    message: types.Message, session: AsyncSession, new_value: list
):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f"➕ Выбранные категории для добавления: {new_value}",
            reply_markup=await get_keyboard_fab(session),
        )


@router.message(F.text.lower() == "подписаться на уведомления")
async def with_puree_fab(message: types.Message, session: AsyncSession):
    user_data[message.from_user.id] = defaultdict()
    await message.answer(
        "Выберите категорию уведомлений:", reply_markup=await get_keyboard_fab(session)
    )


@router.callback_query(NotificationCallbackFactory.filter())
async def callbacks_notification_change_fab(
    callback: types.CallbackQuery,
    callback_data: NotificationCallbackFactory,
    session: AsyncSession,
):

    user_value = user_data.get(callback.from_user.id, defaultdict())

    if callback_data.action == "change":
        user_value = del_or_add(
            user_value, callback_data.value, callback_data.description
        )
        user_list = list(user_value.values())
        await update_notification_text_fab(callback.message, session, user_list)

    else:
        await add_notifications(session, user_value, callback.from_user.id)
        user_list = list(user_value.values())
        await callback.message.edit_text(
            f"Успешно подписались на следующие уведомления: {user_list}"
        )
