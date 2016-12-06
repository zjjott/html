# coding=utf-8
from __future__ import unicode_literals
from celery import Celery
import apps.conf  # flake8: noqa
from tornado.options import options

app = Celery('asynctask')
app.autodiscover_tasks(['apps.asynctask'])
app.config_from_object('tornado.options:options')