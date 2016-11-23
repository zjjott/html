# coding=utf-8
from __future__ import unicode_literals
from tornado.gen import coroutine, Return
from apps.core.views import BaseHandler
from tornado.options import options
from apps.core.httpclient import BAHTTPClient
from simplejson import loads
import urlparse
from urllib import urlencode
from tornado.web import HTTPError
from random import random


class UserAuthBaseHandle(BaseHandler):

    @coroutine
    def prepare(self):
        super(UserAuthBaseHandle, self).prepare()
        if not hasattr(self, "_current_user"):  # 提前使用异步方法对用户进行赋值
            self._current_user = yield self.get_current_user_async()

    @coroutine
    def get_current_user_async(self):
        if hasattr(self.request, "session"):
            user_id = self.request.session['user_id']
            if user_id:
                return user_id
        raise Return(None)

    def get_current_user(self):
        """从session中获得用户信息
        """
        raise NotImplementedError("这个方法不应该被调用，参考get_current_user_async方法")


class UserAuthHandle(UserAuthBaseHandle):
    """需要用户登录的视图基类"""
    @coroutine
    def prepare(self):
        # 先准备session和用户
        result = super(UserAuthHandle, self).prepare()
        if result is not None:
            result = yield result
        # 再检查用户
        if not self.current_user:
            if self.request.method in ("GET", "HEAD"):
                url = self.get_login_url()
                if "?" not in url:
                    if urlparse.urlsplit(url).scheme:
                        # if login url is absolute, make next absolute too
                        next_url = self.request.full_url()
                    else:
                        next_url = self.request.uri
                    url += "?" + urlencode(dict(next=next_url))
                self.redirect(url)
                return
            raise HTTPError(403)


class UserAuthAjaxHandle(UserAuthBaseHandle):
    """需要用户登录的Ajax视图基类"""

    def handle_auth_fail(self):
        """可以重载，以支持不同的回调类型"""
        self.json_error_respon("登录已过期", code=401,)
        return

    @coroutine
    def prepare(self):
        # 先准备session
        result = super(UserAuthAjaxHandle, self).prepare()
        if result is not None:
            result = yield result
        # 再检查用户
        if not self.current_user:
            self.handle_auth_fail()


class LoginHandler(BaseHandler):

    @coroutine
    def get(self):
        return


class LogoutHandler(UserAuthBaseHandle):

    def get(self):
        """登出理应是post的,有csrf问题呢"""
        self.request.session.clear()
        self.clear_all_cookies()
        url = self.reverse_url("login")
        return self.redirect(url)


class CallbackHandler(BaseHandler):

    @coroutine
    def fetch_user(self, token):
        client = BAHTTPClient(options.mt_user_id,
                              options.mt_user_secret,
                              options.mt_sso_host)
        response = yield client.get(options.mt_sso_userinfo,
                                    {"token": token,
                                     'appid': 'mos',
                                     'fields': 'username,email,mobile,id'})
        if response.code != 200:
            raise Return({'code': response.code,
                          'message': '登录失败:%s',
                          })
        try:
            respon = loads(response.body)
        except Exception, e:
            raise Return({'code': 500,
                          'message': '登录错误:%s' % e,
                          })
        if 'error' in respon:
            respon = respon['error']
        respon['code'] = response.code
        raise Return(respon)

    @coroutine
    def post(self):  # 免登陆
        self.request.session['user_id'] = random() * 1000
