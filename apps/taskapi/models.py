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

    def to_dict(self):
        obj_dict = super(MLMethod, self).to_dict()
        obj_dict['kwargs'] = [i.to_dict() for i in self.kwargs]
        return obj_dict


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
    type = Column(NoConstraintEnum(*[
        "int",
        "list"
    ]), doc="参数类型验证"
    )