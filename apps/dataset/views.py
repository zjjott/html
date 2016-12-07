# coding=utf-8
from __future__ import unicode_literals
from apps.auth.views import UserAuthAjaxHandle
from apps.dataset.models import DatasetModel


class ListDataView(UserAuthAjaxHandle):

    def get(self):
        query = DatasetModel.list()
        result = []
        fields = ['id', 'name',
                  'description', 'type']
        result = [dict(zip(fields, i)) for i in query.all()]

        return self.json_respon(result)


class DataPreviewView(UserAuthAjaxHandle):

    def get(self, id):
        dataset = DatasetModel.query().get(id)
        if dataset:
            pass
        else:
            return self.json_error_respon(code=404)
