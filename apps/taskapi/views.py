# coding=utf-8
from __future__ import unicode_literals
from apps.auth.views import UserAuthAjaxHandle
from apps.asynctask import app
from apps.taskapi.models import MethodKwargs, MLMethod
from apps.taskapi.forms import (ListMethodForm, form_factory)
from sqlalchemy.sql.expression import or_, and_
from cPickle import loads, dumps, HIGHEST_PROTOCOL
from tornado.web import asynchronous
from apps.asynctask import app as celery_app
from tornado.ioloop import IOLoop
from apps.asynctask.tasks import CustomerTrainTask


class ListQueueView(UserAuthAjaxHandle):

    def get(self):
        controler = app.control.inspect()
        result = {}
        stats = controler.stats()
        for server, usage in stats.iteritems():
            result[server] = usage["pool"]["writes"]["inqueues"]
        return self.json_respon(result)


class TaskDetail(UserAuthAjaxHandle):

    def get(self, task_id):
        meta = celery_app.backend.get_task_meta(task_id)
        for key, value in meta.iteritems():
            if isinstance(value, Exception):
                meta[key] = str(value)
        return self.json_respon(meta)


class ListMethodView(UserAuthAjaxHandle):

    def get(self):
        form = ListMethodForm(self)
        if form.validate():
            cleaned_data = form.data
            query = MLMethod.query(
                MLMethod.id,
                MLMethod.name,
                MLMethod.description,
            )
            public = cleaned_data['public']
            if public:
                query = query.filter_by(public=True)
            else:
                query = query.filter_by(
                    public=False,
                    user_id=self.current_user)
            trained = cleaned_data['trained']
            query = query.filter_by(trained=trained)
            return self.json_respon([{
                "id": id,
                "name": name,
                "description": description,

            } for id, name, description in query])
        else:
            return self.json_error_respon(form.error)


class MethodDetailView(UserAuthAjaxHandle):

    def filter_query(self, query):
        query = query.filter(or_(MLMethod.public,
                                 and_(~MLMethod.public,
                                      MLMethod.user_id == self.current_user)))
        return query

    def get(self, id):
        query = MLMethod.query(
            MLMethod.id,
            MLMethod.name,
        ).filter_by(id=id)
        query = self.filter_query(query)
        method = query.first()
        if not method:
            return self.json_error_respon("method not found", code=404)
        id, name = method
        obj = {
            "id": id,
            "name": name
        }
        # 没法用预取了
        obj['kwargs'] = [i.to_dict()
                         for i in MethodKwargs.query().filter_by(model_id=id)]
        return self.json_respon(obj)

    def wait_result(self, result):
        if result.ready():
            self.on_result(result.get())
        else:
            io_loop = IOLoop.current()
            io_loop.add_timeout(1000, self.wait_result, result)

    @asynchronous
    def post(self, id):
        query = MLMethod.query()
        query = self.filter_query(query)
        method = query.filter_by(id=id).first()
        if not method:
            return self.json_error_respon(
                "method not found", code=404)
        form_class = form_factory(method.kwargs)
        form = form_class(self)
        if form.validate():
            cleaned_data = form.data
            action = cleaned_data.pop("action", "train")
            sync = cleaned_data.pop("sync", False)
            if action == "predict" and method.trained:
                task = loads(method.data)
                if isinstance(task, tuple):
                    task = task[0]
                    result = task.apply_async(
                        args=[id],
                        kwargs=cleaned_data)
                else:
                    result = task.apply_async(kwargs=cleaned_data)
                if sync:
                    self.wait_result(result)
                else:
                    return self.json_respon(result.task_id)
            elif action == "train":
                dataset = cleaned_data.get("dataset")
                if dataset:
                    CustomerTrainTask.apply_async(args=[
                        dataset,
                        id,
                        self.current_user
                    ], kwargs=cleaned_data)
                    self.json_respon(cleaned_data)
                else:
                    pass
            else:
                return self.json_error_respon("确定你提交了一个可以预测的模型或者可以训练的模型")
        else:
            return self.json_error_respon(form.errors)

    def on_result(self, result):
        self.json_respon(result)
