# coding=utf-8
from __future__ import unicode_literals
from tornado.web import RequestHandler
from tornado.gen import coroutine
from tornado.util import import_object
from tornado.options import options
from apps.core.models.base import clean_db_session
from raven.contrib.tornado import SentryMixin


class JSONBaseHandler(SentryMixin, RequestHandler):

    def json_respon(self, json=None, code=200, **kwargs):
        """保证返回的一定是个dict,list会导致信息泄露风险
        RequestHandler.write文档里写得
        """
        if json is not None:
            result = {"data": json, "code": code}
        else:
            result = {"code": code}
        result.update(kwargs)
        self.add_header("Content-Type", "application/json")
        self.write(result)
        self.finish()

    def json_raw(self, data):
        self.add_header("Content-Type", "application/json")
        self.write(data)
        self.finish()

    def json_error_respon(self, json=None, code=400, **kwargs):
        if json is not None:
            result = {"error": json, "code": code}
        else:
            result = {"code": code}
        result.update(kwargs)
        self.add_header("Content-Type", "application/json")
        self.write(result)
        self.finish()

    def captureException(self, *args, **kwargs):
        if not options.debug:
            super(JSONBaseHandler, self).captureException(*args, **kwargs)


class BaseHandler(JSONBaseHandler):
    """原始响应基类"""

    @coroutine
    def prepare(self):
        """准备session存储"""
        session_class = import_object(options.session_engine)
        session_id = self.get_cookie('tsession',
                                     )
        if not session_id:
            session_id = session_class.new_session_id()
            self.request.session = session_class(self,
                                                 session_id)
            self.set_cookie('tsession',
                            session_id,
                            expires_days=3)  # 3天session过期？
        else:
            self.request.session = session_class(self,
                                                 session_id)

    def finish(self, chunk=None):
        """保存session"""
        if self.request.session.modified:
            self.request.session.save()
        super(BaseHandler, self).finish(chunk)

    def on_finish(self):
        clean_db_session()

    def get_sentry_user_info(self):
        """
        Data for sentry.interfaces.User

        Default implementation only sends `is_authenticated` by checking if
        `tornado.web.RequestHandler.get_current_user` tests postitively for on
        Truth calue testing
        """
        try:
            user = self.get_current_user()
        except Exception:
            return {}
        return {
            'user': {
                'is_authenticated': True if user else False,
                'username': user.username if user else False,
                'user_id': user.user_id if user else False,
            }
        }



class BAAuthView(RequestHandler):
    pass


class RestfulView(RequestHandler):
    http_method = ['get', 'post', 'put', 'delete']
