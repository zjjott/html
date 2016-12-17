# coding=utf-8
from __future__ import unicode_literals

from apps.core.models.base import ModelBase
from sqlalchemy import (Column, Integer,
                        VARCHAR, Index, BLOB,
                        Boolean,
                        Text)
from sqlalchemy.orm import relationship, backref

from apps.core.models.fields import NoConstraintEnum, JSONField


class MLMethod(ModelBase):
    """用于训练的模型
    """
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)
    name = Column(VARCHAR(length=20))
    description = Column(Text, nullable=True)
    public = Column(Boolean, doc="是否公开")
    trained = Column(Boolean, doc="是否已经完成训练")
    data = Column(BLOB, nullable=True,
                  doc="模型的dump")


class MethodKwargs(ModelBase):
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, doc="归属的模型ID")
    model = relationship("MLMethod",
                         backref=backref("kwargs",
                                         lazy='dynamic',
                                         cascade="delete,delete-orphan",
                                         ),
                         foreign_keys="MethodKwargs.model_id",
                         primaryjoin="MLMethod.id==MethodKwargs.model_id",
                         )
    name = Column(VARCHAR(length=20))
    label = Column(VARCHAR(length=50), nullable=True)
    description = Column(Text, nullable=True)
    required = Column(Boolean)
    type = Column(NoConstraintEnum(*[
        "int",
        "list",
        "image",
        "file",
        "str",
    ]), doc="参数类型"
    )
