# coding=utf-8
from __future__ import unicode_literals
from apps.core.models import ResourceModelBase
from sqlalchemy import Column, Integer, VARCHAR, Index
from apps.core.timezone import human_readable
from sqlalchemy.ext.declarative import declared_attr
from library.utils.encoding import ensure_utf8


class User(ResourceModelBase):
    id = Column(Integer, primary_key=True)
    username = Column(VARCHAR(length=200), nullable=False)
    tenant_id = Column(VARCHAR(length=50), nullable=False)
    user_id = Column(VARCHAR(length=50), nullable=False)

    @staticmethod
    def convert_date2string(date):
        return human_readable(date)

    @declared_attr
    def __table_args__(cls):
        return (Index('idx_tenant_id_user_id',
                      'tenant_id',
                      'user_id'),
                ResourceModelBase.__table_args__)

    def __str__(self):
        return ensure_utf8("%s,%s" % (self.username, self.tenant_id))

    def __unicode__(self):
        return "%s,%s" % (self.username, self.tenant_id)
