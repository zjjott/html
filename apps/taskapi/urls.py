# coding=utf-8
from __future__ import unicode_literals
from apps.taskapi.views import (ListQueueView,
                                ListMethodView,
                                TaskDetail,
                                MethodDetailView)
from apps.core.urlutils import urlpattens
routes = [
    (r"/queue/", ListQueueView, None, 'queue'),
    (r"/task/(?P<task_id>[\w-]+)", TaskDetail, None, 'task'),
    (r"/method/", ListMethodView, None, 'method'),
    (r"/method/(?P<id>\d+)/", MethodDetailView, None, 'detail'),
]

urls = urlpattens('task', routes)
