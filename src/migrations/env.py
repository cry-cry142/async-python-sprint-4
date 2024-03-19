import os
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from dotenv import load_dotenv

from models.base import Base
from core.config import ENV_PATH

# dir_env = os.path.normpath(
#     os.path.join(os.path.dirname(__file__), '..', '.env')
# )

load_dotenv(ENV_PATH)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

config.set_main_option('sqlalchemy.url', os.environ['DATABASE_DSN'])
# config.set_main_option('prepend_sys_path', 'src')
# sys_path = config.get_main_option('prepend_sys_path')
# print('>>>>>>>>>>>>>' + sys_path)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def render_item(type_, obj, autogen_context):
    if (
        type_ == 'type'
        and obj.__class__.__module__.startswith('sqlalchemy_utils.')
    ):
        module, _ = obj.__class__.__module__.split('.', 1)
        autogen_context.imports.add(f'import {module}')
        if hasattr(obj, 'choices'):
            return (
                f'{obj.__class__.__module__}.{obj.__class__.__name__}'
                f'(choices={obj.choices})'
            )
        else:
            return f'{obj.__class__.__module__}.{obj.__class__.__name__}()'
    return False


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_item=render_item
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_item=render_item
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

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
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
