# coding=utf-8
from __future__ import unicode_literals
from apps.core.form import TornadoForm
from wtforms import fields


class ListMethodForm(TornadoForm):
    public = fields.BooleanField()
    trained = fields.BooleanField()
