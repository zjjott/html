# coding=utf-8
from __future__ import unicode_literals
from apps.core.form import TornadoForm, ListField
from wtforms import fields
from wtforms import validators
from wtforms.validators import ValidationError
from wtforms.form import FormMeta
from tornado.httputil import HTTPFile
from StringIO import StringIO
from apps.dataset.models import DatasetModel


class ListMethodForm(TornadoForm):
    public = fields.BooleanField()
    trained = fields.BooleanField()


class MethodActionForm(TornadoForm):
    dataset = fields.SelectField(
        coerce=int,
        validators=[validators.Optional()])
    action = fields.SelectField(choices=[
        ("train", "train"),
        ("predict", "predict"),
    ])
    sync = fields.BooleanField()
    file = fields.FileField(validators=[validators.Optional()])
    data = fields.StringField(validators=[validators.Optional()])

    def __init__(self, *args, **kwargs):
        super(MethodActionForm, self).__init__(*args, **kwargs)
        self.dataset.choices = [(id, id)
                                for (id,) in DatasetModel.query(DatasetModel.id)]

    @classmethod
    def validate_action(cls, form, field):
        data = form.data
        if data.get("action") == "train" and not data.get("dataset"):
            raise ValidationError("需要提供训练的数据集")

    @property
    def data(self):
        data = super(MethodActionForm, self).data
        for key, value in data.iteritems():
            if isinstance(value, HTTPFile):
                data[key] = StringIO(value.body)
        return data

SELECT_FIELD_MAP = {
    "int": fields.IntegerField,
    "list": ListField,
    "image": fields.FileField,
}


def form_factory(kwargs,
                 base=MethodActionForm,
                 name=b"DynamicForm"):
    """动态form生成函数，
    """
    fields = {}
    for kw in kwargs:
        _type = kw.type
        v = []
        if kw.required:
            v.append(validators.Required())
        else:
            v.append(validators.Optional())

        fields[kw.name] = SELECT_FIELD_MAP[_type](validators=v)
    form_class = FormMeta(name, (base,), fields)
    return form_class
