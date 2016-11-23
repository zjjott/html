# coding=utf-8
from __future__ import unicode_literals
from sqlalchemy.types import (TypeDecorator, DateTime,
                              Text, Enum, Date)
from pytz import UTC
from tornado.options import options
from simplejson import loads, dumps
from sqlalchemy.ext.mutable import Mutable
from wtforms.ext.sqlalchemy.orm import ModelConverter, converts
from datetime import date


class AwareDateTime(TypeDecorator):
    '''Prefixes Unicode values with "PREFIX:" on the way in and
    strips it off on the way out.
    '''

    impl = DateTime

    def process_bind_param(self, value, dialect):
        """放入数据库"""
        if value is not None and isinstance(value, date):
            if value.tzinfo:  # 差6分钟问题
                value = value.astimezone(UTC)
            else:
                value = value.replace(tzinfo=UTC)

        return value

    def process_result_value(self, value, dialect):
        """从数据库取出并变成Python对象,UTC->+8"""
        if value is not None and isinstance(value, date):
            if not value.tzinfo:
                value = value.replace(tzinfo=UTC)
            value = value.astimezone(options.tz)
        return value


class CustomerModelConverter(ModelConverter):

    @converts('AwareDateTime')
    def conv_AwareDateTime(self, field_args, **extra):
        return self.conv_DateTime(field_args, **extra)


class MutableDict(Mutable, dict):

    def __str__(self):
        return dumps(self)

    def __getstate__(self):
        """picker dumps"""
        return dict(self)

    def __setstate__(self, state):
        self.update(state)

    @classmethod
    def coerce(cls, key, value):
        "Convert plain dictionaries to MutableDict."

        if not isinstance(value, MutableDict):
            if isinstance(value, basestring):
                if value:
                    value = value.strip()
                    value = loads(value)
                else:
                    value = {}
            if isinstance(value, dict):
                return MutableDict(value)

            # this call will raise ValueError
            return Mutable.coerce(key, value)
        else:
            return value

    def __setitem__(self, key, value):
        "Detect dictionary set events and emit change events."

        dict.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        "Detect dictionary del events and emit change events."

        dict.__delitem__(self, key)
        self.changed()


class JSONField(TypeDecorator):
    impl = Text

    def process_bind_param(self, value, dialect):
        """放入数据库"""
        if value is not None:
            if isinstance(value, (dict, list)):
                value = dumps(value)
        else:
            value = dumps({})
        return value

    def process_result_value(self, value, dialect):
        """从数据库取出并变成Python对象,UTC->+8"""
        if value is not None:
            if isinstance(value, basestring):
                value = loads(value)
        if value is None:
            value = {}
        return value
# 使得对JSONField dict元素的修改，触发session dirty
MutableDict.associate_with(JSONField)


class NoConstraintEnum(Enum):

    def __init__(self, *enums, **kw):
        kw['native_enum'] = False
        super(NoConstraintEnum, self).__init__(*enums, **kw)

    def _should_create_constraint(self, compiler):
        return False

fields = {"AwareDateTime",
          "JSONField",
          "NoConstraintEnum",
          }  # 给alembic用的
