# coding=utf-8
from __future__ import unicode_literals
from apps.dataset.views import (ListDataView, DataPreviewView)
from apps.core.urlutils import urlpattens
routes = [
    (r"/", ListDataView, None, 'list'),
    (r"/(?P<id>\d+)/", DataPreviewView, None, 'preview'),
]

urls = urlpattens('data', routes)
