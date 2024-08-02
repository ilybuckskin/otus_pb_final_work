from collections import defaultdict
from contextlib import suppress
from typing import Optional

from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from db.requests import get_user_notifications, unsubscribe_notifications
from sqlalchemy.ext.asyncio import AsyncSession

router = Router(name="Management Notification Router")

user_data = {}


class ManagementNotificationCallbackFactory(CallbackData, prefix="mng_notif"):
    action: str
    value: Optional[int] = None
    description: Optional[str] = None


async def get_keyboard_fab(session: AsyncSession, user_id: int):
    notifications = await get_user_notifications(session, user_id)
    builder = InlineKeyboardBuilder()
    for i in notifications:
        builder.button(
            text=str(i.notification_name),
            callback_data=ManagementNotificationCallbackFactory(
                action="change",
                value=i.notification_id,
                description=i.notification_name,
            ),
        )
    builder.button(
        text="⬅️ Отмена",
        callback_data=ManagementNotificationCallbackFactory(action="finish"),
    )
    builder.button(
        text="❌ Отписаться",
        callback_data=ManagementNotificationCallbackFactory(action="unsubscribe"),
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
    message: types.Message, session: AsyncSession, new_value: list, user_id: int
):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f"❌ Выбранные категории для удаления: {new_value}",
            reply_markup=await get_keyboard_fab(session, user_id),
        )


@router.message(F.text.lower() == "проверить подписки")
async def with_puree_fab(message: types.Message, session: AsyncSession):
    user_data[message.from_user.id] = defaultdict()
    await message.answer(
        "Вы подписаны на следующие уведомления, для удаления выберите уведомления из списка:",
        reply_markup=await get_keyboard_fab(session, message.from_user.id),
    )


@router.callback_query(ManagementNotificationCallbackFactory.filter())
async def callbacks_notification_change_fab(
    callback: types.CallbackQuery,
    callback_data: ManagementNotificationCallbackFactory,
    session: AsyncSession,
):
    user_value = user_data.get(callback.from_user.id, defaultdict())
    print(callback_data.action)
    if callback_data.action == "change":
        user_value = del_or_add(
            user_value, callback_data.value, callback_data.description
        )
        user_list = list(user_value.values())
        await update_notification_text_fab(
            callback.message, session, user_list, callback.from_user.id
        )
    elif callback_data.action == "unsubscribe":
        await unsubscribe_notifications(session, user_value, callback.from_user.id)
        user_list = list(user_value.values())
        await callback.message.edit_text(f"Успешно отписались от следующих уведомлений: {user_list}")
    else:
        await callback.message.edit_text(f"Спасибо, что воспользовались ботом!")
