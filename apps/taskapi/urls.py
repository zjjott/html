# coding=utf-8
from __future__ import unicode_literals
from apps.taskapi.views import (ListQueueView,
                                ListMethodView,
                                MethodDetailView)
from apps.core.urlutils import urlpattens
routes = [
    (r"/queue/", ListQueueView, None, 'queue'),
    (r"/method/", ListMethodView, None, 'method'),
    (r"/method/(?P<id>\d+)/", MethodDetailView, None, 'detail'),
]

urls = urlpattens('task', routes)
