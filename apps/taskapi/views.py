# coding=utf-8
from __future__ import unicode_literals
from apps.auth.views import UserAuthAjaxHandle
from apps.asynctask import app


class ListQueueView(UserAuthAjaxHandle):

    def get(self):
        controler = app.control.inspect()
        result = {}
        stats = controler.stats()
        for server, usage in stats.iteritems():
            result[server] = usage["pool"]["writes"]["inqueues"]
        return self.json_respon(result)
