# coding=utf-8
from __future__ import unicode_literals
from apps.auth.views import UserAuthAjaxHandle
from apps.asynctask import app
from apps.taskapi.models import MethodKwargs, MLMethod
from apps.taskapi.forms import ListMethodForm


class ListQueueView(UserAuthAjaxHandle):

    def get(self):
        controler = app.control.inspect()
        result = {}
        stats = controler.stats()
        for server, usage in stats.iteritems():
            result[server] = usage["pool"]["writes"]["inqueues"]
        return self.json_respon(result)


class ListMethodView(UserAuthAjaxHandle):

    def get(self):
        form = ListMethodForm(self)
        if form.validate():
            cleaned_data = form.data
            query = MLMethod.query()
            public = cleaned_data['public']
            if public:
                query = query.filter_by(public=True)
            else:
                query = query.filter_by(
                    public=False,
                    user_id=self.current_user)
            trained = cleaned_data['trained']
            query = query.filter_by(trained=trained)
            return self.json_respon([i.to_dict() for i in query])
        else:
            return self.json_error_respon(form.error)
