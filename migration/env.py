from aiogram_bot.database.db import DB_URL
from aiogram_bot.database.models import Base
from alembic import context
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy.engine import Connection
from sqlalchemy import pool
from logging.config import fileConfig
import asyncio
import sys
from os.path import dirname, abspath

sys.path.insert(0, dirname(dirname(abspath(__file__))))


# Импортируем Base из файла моделей


# это объект конфигурации Alembic, который предоставляет
# доступ к параметрам в используемом .ini файле.
config = context.config

# Интерпретируем файл конфигурации для логирования Python.
# Эта строка настраивает логгеры.
if config.config_file_name is not None:
    config.set_main_option("sqlalchemy.url", DB_URL)
    fileConfig(config.config_file_name)

# Добавляем объект MetaData ваших моделей для поддержки 'autogenerate'
# target_metadata — это метаданные всех ваших моделей
target_metadata = Base.metadata

# Другие значения из конфигурации, определенные потребностями env.py,
# могут быть получены так:
# my_important_option = config.get_main_option("my_important_option")
# ... и так далее.


def run_migrations_offline() -> None:
    """Запуск миграций в режиме 'offline'.

    Это конфигурирует контекст только с URL
    и без создания Engine. Это позволяет запускать миграции
    без необходимости подключения к базе данных через DBAPI.

    Вызовы context.execute() здесь генерируют миграции, выводимые как SQL.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Выполнение миграций с установленным соединением"""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """В этом сценарии необходимо создать движок
    и ассоциировать соединение с контекстом миграции.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Запуск миграций в режиме 'online'."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
