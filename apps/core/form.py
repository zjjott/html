# coding=utf-8
from __future__ import unicode_literals
from wtforms.form import Form
from wtforms.compat import iteritems
from wtforms.validators import ValidationError
from simplejson import loads
from wtforms.fields import SelectField, FileField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from datetime import date, timedelta
from apps.core.const import DATE_RANGE
from wtforms import widgets
from wtforms.compat import text_type
from wtforms.widgets import TableWidget
import re
try:
    from html import escape
except ImportError:
    from cgi import escape
from cStringIO import StringIO
from openpyxl import load_workbook
from wtforms.widgets.core import html_params, HTMLString


class TornadoFormWrap(object):

    def __init__(self, handler):
        self.arguments = handler.request.arguments
        self.files = handler.request.files

    def getlist(self, name):
        return self.arguments.get(name,
                                  self.files.get(name))

    def __iter__(self):
        for v in self.arguments:
            yield v
        for f in self.files:
            yield f

    def __len__(self):
        return len(self.arguments) + len(self.files)

    def __contains__(self, name):
        # We use request.arguments because get_arguments always returns a
        # value regardless of the existence of the key.
        return (name in self.arguments) or (name in self.files)


def flat_list(l):
    if isinstance(l, list):
        return " ".join(l)
    return l


class TableWithErrorWidget(TableWidget):

    def __call__(self, field, **kwargs):
        html = []
        if self.with_table_tag:
            html.append('<table %s>' % html_params(**kwargs))
        hidden = ''
        for subfield in field:
            if subfield.type in ('HiddenField', 'CSRFTokenField'):
                hidden += text_type(subfield)
            else:
                html.append('<tr><th>%s</th><td>%s%s</td></tr>' % (
                    text_type(subfield.label),
                    hidden,
                    text_type(subfield)))
                hidden = ''
            if subfield.errors:  # 渲染错误提示
                html.append('<tr class="has-warning"><th class="text-help">%s</th><td class="text-help">%s</td></tr>' % (
                    text_type(subfield.label),
                    text_type(",".join(subfield.errors))
                ))
        if self.with_table_tag:
            html.append('</table>')
        if hidden:
            html.append(hidden)
        return HTMLString(''.join(html))


class TornadoForm(Form):
    _render = None

    def __init__(self, formdata=None, *args, **kwargs):
        """formdata传入一个handler"""
        super(TornadoForm, self).__init__(TornadoFormWrap(formdata),
                                          *args, **kwargs
                                          )

    @property
    def errors(self):
        """展平error"""
        if self._errors is None:
            self._errors = dict((name, flat_list(f.errors)
                                 )
                                for name, f in iteritems(self._fields
                                                         ) if f.errors)
        return self._errors

    @property
    def data(self):
        """DateRangeField一次提供了多个name"""
        value_map = []
        for name, field in iteritems(self._fields):
            if isinstance(field, DateRangeField):
                # 换成dataset，因为data要用于pre_validate
                for extra_name, value in field.dataset.iteritems():
                    value_map.append((extra_name, value))
            else:
                value_map.append((name, field.data))

        return dict(value_map)

    def render(self, **kwargs):
        if self._render is None:
            self._render = TableWithErrorWidget(with_table_tag=True)
        return self._render(self, **kwargs)


class JSONValidator(object):

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        data = field.data
        if data:
            if not isinstance(data, basestring):
                message = field.gettext("JSON field need string")
                raise ValidationError(message)
            try:
                loads(data)
            except:
                message = field.gettext("invalid json string")
                raise ValidationError(message)
        else:
            field.data = {}


class DateRangeField(SelectField):

    def __init__(self, **kwargs):
        kwargs['choices'] = DATE_RANGE
        kwargs['default'] = "30d"
        super(DateRangeField, self).__init__(**kwargs)

    def _get_start_day(self, choice):
        data = {}
        if choice.endswith("d"):
            days = int(choice[:-1])
            today = date.today()
            start = today - timedelta(days=days)
            data['start'] = start.strftime("%Y%m%d")
            data['moonstart'] = start.replace(day=1).strftime("%Y%m%d")
            data['end'] = today.strftime("%Y%m%d")
            data['datekey'] = today.strftime("%Y%m%d")
        else:  # all
            today = date.today()
            data['start'] = date(2014, 1, 1).strftime("%Y%m%d")
            data['moonstart'] = date(2014, 1, 1).strftime("%Y%m%d")
            data['end'] = today.strftime("%Y%m%d")
            data['datekey'] = today.strftime("%Y%m%d")
        return data

    def process_data(self, value):
        super(DateRangeField, self).process_data(value)
        if self.data:
            self.dataset = self._get_start_day(self.data)

    def process_formdata(self, valuelist):
        super(DateRangeField, self).process_formdata(valuelist)
        if self.data:
            # 换成dataset，因为data要用于pre_validate
            self.dataset = self._get_start_day(self.data)


class CheckBoxSelect(widgets.Select):

    def __init__(self):
        pass

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs['class'] = "checkbox"
        html = ['<div %s>' % widgets.html_params(name=field.name,
                                                 **kwargs)]
        for val, label, selected in field.iter_choices():
            html.append(self.render_option(
                val, label, selected, name=field.name))
        html.append('</div>')
        return widgets.HTMLString(''.join(html))

    @classmethod
    def render_option(cls, value, label, selected, **kwargs):
        if value is True:
            # Handle the special case of a 'True' value.
            value = text_type(value)

        options = dict(kwargs, value=value)
        if selected:
            options['checked'] = True
        options.setdefault("type", 'checkbox')
        return widgets.HTMLString('<label><input %s />%s</label>' % (
            widgets.html_params(**options),
            escape(text_type(label), quote=False)))


class QueryCheckMultipleField(QuerySelectMultipleField):
    widget = widgets.Select()


class ExcelFileField(FileField):
    excel_filename = re.compile(r".*\.xlsx?$")

    def process_formdata(self, valuelist):
        super(ExcelFileField, self).process_formdata(valuelist)
        data = self.data
        if self.data:
            if not ('content_type' in data and
                    data['content_type'].endswith("sheet")):
                raise ValidationError("文件类型不合法：不是excel文件")
            if 'filename' in data and not re.search(
                    self.excel_filename,
                    data['filename']):
                raise ValidationError("文件名不合法：请上传2010版本以上的xlsx文件")
            filelike = StringIO(data.body)
            filelike.seek(0)
            try:
                excel = load_workbook(filelike, read_only=True)
            except Exception:
                raise ValidationError("请上传2010版本以上的xlsx文件")
            else:
                self.data = excel


class TornadoFileField(FileField):
    """使得Tornado FileStorage 被wtform支持"""

    def process_formdata(self, valuelist):
        super(TornadoFileField, self).process_formdata(valuelist)
        if self.data and isinstance(self.data, dict):
            self.data = self.data["filename"]
