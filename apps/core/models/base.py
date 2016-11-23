# coding=utf-8
from __future__ import unicode_literals
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (scoped_session, sessionmaker,
                            Session as BaseSession, object_mapper)
from sqlalchemy import (Column,
                        Boolean, BigInteger,
                        VARCHAR)

from library.utils.time import isotime, get_utcnow
from tornado.options import options
import apps.conf  # flake8: noqa
import random
from datetime import date
from sqlalchemy import create_engine
from apps.core.models.fields import AwareDateTime, MutableDict
import logging
from sqlalchemy.ext.declarative import declared_attr

from sqlalchemy.types import TypeDecorator
from sqlalchemy.ext.serializer import loads, dumps
logger = logging.getLogger("sqlalchemy")
BASEOBJ = declarative_base()


class ModelBase(BASEOBJ):
    """Base class for Nova and Glance Models"""
    __abstract__ = True
    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mysql_charset': 'utf8'}
    __table_initialized__ = False

    @classmethod
    def get_session(cls):
        return master_db()

    def save_object(self, session=None, commit=True):
        """Save a new object"""
        if session is None:
            session = master_db()
        session.add(self)
        if commit:
            try:
                session.commit()
            except:
                session.rollback()
                # clean_db_session()
                raise

    def insert_for_update(self, session=None):
        """实质是根据主键select，然后save"""
        if session is None:
            session = master_db()
        new_instance = session.merge(self)
        session.add(new_instance)
        try:
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            clean_db_session()

    def save_updates(self, session=None):
        """Save a new object"""
        if session is None:
            session = master_db()
        session.add(self)
        try:
            session.commit()
        except:
            session.rollback()
            # clean_db_session()
            raise

    def delete_phys(self):
        """Remove the object"""
        session = master_db()
        session.delete(self)
        try:
            session.commit()
        except:
            session.rollback()
            raise
        # finally:
            # clean_db_session()

    @classmethod
    def query(cls, *args, **kwargs):
        """ Query """
        if kwargs.get("master"):  # 强制查事务中的session
            session = master_db()
        else:
            session = slave_db()
        if len(args) == 0:
            q = session.query(cls)
        else:
            q = session.query(*args)
        return q

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def populate_dict(self, d):
        for key, value in d.items():
            self[key] = value

    def __iter__(self):
        # TODO:对sql字段名和ORM属性名不一样的情况需要处理
        self._i = iter(object_mapper(self).columns)
        return self

    def next(self):
        n = self._i.next().name
        return n, getattr(self, n)

    def keys(self):
        return [key for key, value in self]

    def dumps(self):
        return dumps(self)

    @classmethod
    def loads(cls, binary_data):
        return loads(binary_data)

    def values(self):
        return [value for key, value in self]

    def items(self):
        return [(key, value) for key, value in self]

    @classmethod
    def create_or_get(cls, **kwargs):
        """
        形如Django create_or_get
        返回obj,is_created
        """
        defaults = kwargs.pop("defaults", {})
        # 判断两个以上有点浪费SQL数量，不写了
        query = cls.query(cls).filter_by(**kwargs)
        obj = query.first()
        if obj:
            return obj, False
        else:
            attr_dict = {}
            attr_dict.update(defaults)
            attr_dict.update(kwargs)
            obj = cls(**attr_dict)
            obj.save_object()
            return obj, True

    @classmethod
    def update_or_create(cls, **kwargs):
        """
        形如Django update_or_create
        kwargs:
            defaults:dict类型，用于更新的字段
            其他字段是用来过滤的
        如果不存在，会创造一个带有kwargs所有字段的对象
        返回obj,is_created
        """
        defaults = kwargs.pop("defaults", {})
        # 判断两个以上有点浪费SQL数量，不写了
        query = cls.query(cls).filter_by(**kwargs)
        obj = query.first()
        if obj:
            for key, value in defaults.iteritems():
                if getattr(obj, key) != value:
                    setattr(obj, key, value)
            write_db = master_db()
            read_db = slave_db()
            if obj in write_db.dirty or obj in read_db.dirty:  # 如果修改过则保存
                obj.save_object()
            return obj, False
        else:
            attr_dict = {}
            attr_dict.update(defaults)
            attr_dict.update(kwargs)
            obj = cls(**attr_dict)
            obj.save_object()
            return obj, True

    @staticmethod
    def convert_date2string(date):
        return isotime(date)

    def to_dict(self, show_time=False):
        ret = {}
        for k, v in self:
            if v is None:
                ret[k] = None
            elif isinstance(v, MutableDict):
                v = dict(v)
            elif isinstance(v, date):
                if not show_time:
                    continue
                v = self.convert_date2string(v)
            elif not isinstance(v, (basestring, str,
                                    unicode, long,
                                    int, float)):
                v = r'%s' % v
            ret[k] = v
        return ret

    @classmethod
    def get_column_def(cls, colname):
        for c in cls.__table__.columns:
            if c.name == colname:
                return c
        return None

    @classmethod
    def is_column_string(cls, col):
        if hasattr(col.type, 'charset'):
            return True
        else:
            return False

    @classmethod
    def is_searchable(cls, col, is_chs):
        coltype = col.type
        if isinstance(coltype, TypeDecorator):
            coltype = coltype.impl
        if coltype.python_type == str and \
                (not is_chs or
                 (hasattr(coltype, 'charset') and coltype.charset == 'utf8')):
            return True
        return False

    @declared_attr
    def __tablename__(cls):
        """可以在类定义里面设定__tablename__=xxx或者从这里默认构造出一个表名"""
        class_name = cls.__name__.lower()
        if class_name.endswith("s"):
            return "%s_tbl" % class_name
        else:
            return "%ss_tbl" % class_name


class ResourceModelBase(ModelBase):
    __abstract__ = True
    created_at = Column('created_at',
                        AwareDateTime, default=get_utcnow,
                        nullable=False, index=True)
    updated_at = Column('updated_at',
                        AwareDateTime, default=get_utcnow,
                        nullable=False, onupdate=get_utcnow)
    deleted_at = Column('deleted_at',
                        AwareDateTime)


__master_engine = None
__slave_engines = None


def _get_master_engine():
    global __master_engine
    if __master_engine is None:
        __master_engine = _create_engine(options.sql_connection)
    return __master_engine


def _get_slave_engine():
    global __master_engine, __slave_engines
    if options.sql_slaves is not None:
        if __slave_engines is None:
            __slave_engines = []
            for desc in options.sql_slaves:
                __slave_engines.append(_create_engine(desc))
        if len(__slave_engines) > 0:
            index = random.randint(0, len(__slave_engines) - 1)
            # logging.info("Using slave db at (%d)", index)
            return __slave_engines[index]
        else:
            return _get_master_engine()
    else:
        # logging.info("No slaves. Using master db")
        return _get_master_engine()


def _create_engine(desc):
    engine_args = {
        'pool_recycle': 360,
        'pool_size': options.db_pool_size,
        'echo': False,
        'convert_unicode': True,
        'logging_name': 'sqlalchemy',
        # 'listeners': [MySQLPingListener()],
    }
    try:
        if options.testing:
            desc = options.test_db
        engine = create_engine(desc, **engine_args)
        engine.connect()
        return engine
    except Exception as e:
        logger.error("Error connect to db engine: %s" % e)
        raise


class RoutingSession(BaseSession):
    # TODO:SQLALchemy ShardedSession

    def get_bind(self, mapper=None, clause=None):
        return _get_master_engine()

    _use_engine = None

    def master(self):
        s = RoutingSession(autocommit=False)
        attrs = vars(self)
        attrs['autocommit'] = False
        vars(s).update(attrs)
        return s

    def slave(self):
        s = RoutingSession(autocommit=True)  # 事务在构造Session时开始
        attrs = vars(self)
        attrs['autocommit'] = True  # autocommit 竟然重复三次心塞。。
        vars(s).update(attrs)
        return s


class WithSessionType(object):
    session_class = None

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __enter__(self):
        self.session = self.session_class(**self.kwargs)
        return self.session

    def __exit__(self, *exc_info):
        # session.close:
        # Close this Session.
        # This clears all items and ends any transaction in progress.
        # If this session were created with autocommit=False,
        # a new transaction is immediately begun.
        # Note that this new transaction does not use any connection resources
        # until they are first needed.
        self.session.close()


def WithSession(session_class):
    return type(session_class.__class__.__name__, (WithSessionType,), {
        "session_class": session_class
    })
# autocommit参数默认为False，此时默认在一次session中使用事务
maker = sessionmaker(class_=RoutingSession,
                     expire_on_commit=False,
                     # autoflush=False,
                     # autocommit=False#默认参数False，表示始终使用事务
                     )
Session = scoped_session(maker)


def master_db():
    global Session, _session_records
    maker.configure(autocommit=False)  # 和上面RoutingSession真是缺一不可= =
    s = Session().master()
    return s


def clean_db_session():
    global Session
    Session.close()
    Session.remove()


def slave_db():  # 读不需要加在事务里。。
    maker.configure(autocommit=True)  # 和上面RoutingSession真是缺一不可= =
    s = Session().slave()
    return s
