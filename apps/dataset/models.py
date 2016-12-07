# coding=utf-8
from __future__ import unicode_literals

from apps.core.models.base import ModelBase
from sqlalchemy import (Column, Integer,
                        VARCHAR, Index, BLOB,
                        Text)
from apps.core.models.fields import NoConstraintEnum


class DatasetModel(ModelBase):
    """数据集模型，懒得搞S3了，数据也存mysql里(吧)

    """
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)
    name = Column(VARCHAR(length=20))
    description = Column(Text, nullable=True)
    type = Column(NoConstraintEnum(*['csv',
                                     'picture']))
    target_column = Column(Integer,
                           nullable=True,
                           default=-1,
                           doc="csv文本中，目标所在的列")
    data = Column(BLOB)

    @classmethod
    def list(cls):
        return cls.query(cls.id, cls.name,
                         cls.description, cls.type)
