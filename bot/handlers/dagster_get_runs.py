from aiogram import types, F, Router
from aiogram.utils.formatting import as_list, as_marked_section, Bold, as_key_value
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

from config import get_connection_string_dagster
from db.requests import test_connection

engine_dagster = create_async_engine(url=get_connection_string_dagster(), echo=True)

sessionmaker_dagster = async_sessionmaker(engine_dagster, expire_on_commit=False)

router = Router(name="Dagster Run Router")


async def check_session():
    async with sessionmaker_dagster() as session:
        await test_connection(session)


async def get_runs(session: AsyncSession):
    """
    Получаетает все типы уведомлений
    :param session: объект AsyncSession
    :return: объект Notifications или None
    """
    result = []
    stmt = text("""SELECT t.run_id, pipeline_name, ROUND(CAST(extract(epoch from now()) - start_time AS numeric), 2) as run_time
                FROM public.runs t
                where status = 'STARTED'""")

    for r in await session.execute(stmt):
        content = as_list(
            as_marked_section(
                Bold(f"{r.pipeline_name}:"),
                as_key_value("run_id", r.run_id),
                as_key_value("run_time", r.run_time),
                marker="  ",
            ),
            sep="\n\n",
        )
        result.append(content)
    return result


@router.message(F.text.lower() == "работающие задания")
async def without_puree(message: types.Message):
    async with sessionmaker_dagster() as session:

        runs = await get_runs(session)
        if runs:
            for run in await get_runs(session):
                await message.answer(**run.as_kwargs())
        else:
            await message.answer('Все задания завершены!')
