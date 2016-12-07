# coding=utf-8
from __future__ import unicode_literals
from apps.dataset.views import (ListDataView)
from apps.core.urlutils import urlpattens
routes = [
    (r"/", ListDataView, None, 'list'),
    (r"/(?P<id>\d+)/", ListDataView, None, 'preview'),
]

urls = urlpattens('data', routes)
