from itertools import filterfalse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import BotUser, Notifications, user_notifications


async def get_all_notifications(session: AsyncSession) -> [Notifications]:
    """
    Получаетает все типы уведомлений
    :param session: объект AsyncSession
    :return: объект Notifications или None
    """
    stmt = select(Notifications)
    return await session.scalars(stmt)


async def get_user_list_notifications(session: AsyncSession, user_id: int) -> [str]:
    """
    Получаетает типы уведомлений пользователя
    :param session: объект AsyncSession
    :param user_id: айди пользователя
    :return: объект Notifications или None
    """
    stmt = select(user_notifications.c.notification_id).where(user_notifications.c.bot_user_id == user_id)
    result = [str(r) for r in await session.scalars(stmt)]
    return result


async def get_user_notifications(session: AsyncSession, user_id: int) -> [Notifications]:
    """
    Получаетает типы уведомлений пользователя
    :param session: объект AsyncSession
    :param user_id: айди пользователя
    :return: объект Notifications или None
    """
    stmt = select(Notifications).join(user_notifications).where(user_notifications.c.bot_user_id == user_id)
    return await session.scalars(stmt)


async def get_user_by_id(session: AsyncSession, user_id: int) -> BotUser | None:
    """
    Получает пользователя по его айди.
    :param session: объект AsyncSession
    :param user_id: айди пользователя
    :return: объект BotUser или None
    """
    stmt = select(BotUser).where(BotUser.telegram_id == user_id)
    return await session.scalar(stmt)


async def get_notification_by_id(session: AsyncSession, notification_id: str) -> Notifications | None:
    """
    Получает пользователя по его айди.
    :param session: объект AsyncSession
    :param notification_id: айди типа уведомления
    :return: объект BotUser или None
    """
    stmt = select(Notifications).where(Notifications.notification_id == notification_id)
    return await session.scalar(stmt)


async def ensure_user(session: AsyncSession, user_id: int) -> None:
    """
    Создаёт пользователя, если его раньше не было
    :param session: объект AsyncSession
    :param user_id: айди пользователя
    """
    existing_user = await get_user_by_id(session, user_id)
    if existing_user is not None:
        return
    user = BotUser(telegram_id=user_id)
    session.add(user)
    await session.commit()


async def add_notifications(session: AsyncSession, notifications: dict, user_id: int) -> None:
    """
    Создаёт заказ в СУБД с привязкой к пользователю
    :param session: объект AsyncSession
    :param notifications: данные о необходимых уведомлениях
    :param user_id: айди пользователя
    """

    await ensure_user(session, user_id)

    notifications_list = [str(ids) for ids in notifications.keys()]

    existing_notifications = await get_user_list_notifications(session, user_id)

    add_notifications_list = list(filterfalse(existing_notifications.__contains__,
                                              notifications_list))
    if add_notifications_list:
        bot_user = await get_user_by_id(session, user_id)
        for notification_id in add_notifications_list:
            notification = await get_notification_by_id(session, notification_id)
            bot_user.notifications.append(notification)
            session.add(bot_user)
        await session.commit()


async def unsubscribe_notifications(session: AsyncSession, notifications: dict, user_id: int) -> None:
    """
    Создаёт заказ в СУБД с привязкой к пользователю
    :param session: объект AsyncSession
    :param notifications: данные о необходимых уведомлениях
    :param user_id: айди пользователя
    """

    await ensure_user(session, user_id)

    notifications_list = [str(ids) for ids in notifications.keys()]

    if notifications_list:
        bot_user = await get_user_by_id(session, user_id)
        for notification_id in notifications_list:
            notification = await get_notification_by_id(session, notification_id)
            bot_user.notifications.remove(notification)
            session.add(bot_user)
        await session.commit()

async def test_connection(session: AsyncSession):
    """
    Проверка соединения с СУБД
    :param session: объект AsyncSession
    """
    stmt = select(1)
    return await session.scalar(stmt)
