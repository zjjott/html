# coding=utf-8
from __future__ import unicode_literals
from apps.auth.views import UserAuthAjaxHandle
from apps.dataset.models import DatasetModel
from cStringIO import StringIO
from csv import reader as csv_reader


class ListDataView(UserAuthAjaxHandle):

    def get(self):
        query = DatasetModel.list()
        result = []
        fields = ['id', 'name',
                  'description', 'type']
        result = [dict(zip(fields, i)) for i in query.all()]

        return self.json_respon(result)


class DataPreviewView(UserAuthAjaxHandle):
    LIMIT = 100
    OFFSET = 0

    def get(self, id):
        # memory problem?
        dataset = DatasetModel.query().get(id)
        if dataset:
            if dataset.type == "csv":
                reader = csv_reader(StringIO(dataset.data))
                headers = next(reader)
                data = [row for row in reader]
                total = len(data)
                data = data[self.OFFSET:self.LIMIT]
            return self.json_respon(data,
                                    meta={
                                        "limit": self.LIMIT,
                                        "offset": self.OFFSET,
                                        "headers": headers,
                                        "total": total
                                    })
        else:
            return self.json_error_respon(code=404)
