# coding=utf-8
from __future__ import unicode_literals
from apps.taskapi.views import (ListQueueView)
from apps.core.urlutils import urlpattens
routes = [
    (r"/queue/", ListQueueView, None, 'queue'),
]

urls = urlpattens('task', routes)
