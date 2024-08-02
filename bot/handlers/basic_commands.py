from aiogram import types, Router
from aiogram.filters.command import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

from db.requests import ensure_user

router = Router(name="Basic Commands Router")


@router.message(CommandStart())
async def cmd_start(message: types.Message, session: AsyncSession):
    kb = [
        [
            types.KeyboardButton(text="Подписаться на уведомления"),
            types.KeyboardButton(text="Проверить подписки"),
            types.KeyboardButton(text="Работающие задания")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )
    await ensure_user(session, message.from_user.id)
    await message.answer("Какие действия хотите выполнить?", reply_markup=keyboard)
