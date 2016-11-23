# coding=utf-8
from __future__ import with_statement, unicode_literals, absolute_import
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
import sys
import os
from tornado.options import options

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
dirname = os.path.dirname
abspath = os.path.abspath
app_path = abspath(dirname(dirname(__file__)))
sys.path.insert(0, app_path)
from apps.core.models import ModelBase, _get_master_engine
# 导入需要被自动监测的Model
from apps.models import *

from apps.core.models.fields import fields

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = ModelBase.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = options.sql_connection
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def my_render_item(type_, obj, autogen_context):
    """修改这个方法，以在自动生成脚本的时候，增加import"""
    # 沉思，放外面的时候
    # 不能用isinstance(obj, AwareDateTime),因为 AwareDateTime 已经是个None
    # 被重写掉了。。神奇。。
    fields = autogen_context.opts['fields']
    if type_ == 'type':
        class_name = obj.__class__.__name__
        if class_name in fields:
            # add import for this type
            autogen_context.imports.add(
                "from apps.core.models.fields import %s" % class_name)
            return "%r" % obj

    # default rendering for other objects
    return False


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = _get_master_engine()
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # user_module_prefix="apps.core.models.fields.",
            render_item=my_render_item,
            fields=fields,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
