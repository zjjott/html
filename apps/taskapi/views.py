# coding=utf-8
from __future__ import unicode_literals
from apps.auth.views import UserAuthAjaxHandle
from apps.asynctask import app


class ListQueueView(UserAuthAjaxHandle):

    def get(self):
        return self.json_respon(app.control.ping())
