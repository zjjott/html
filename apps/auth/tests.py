# coding=utf-8
from __future__ import unicode_literals
from apps.core.test import BaseTestCase
from apps.auth.models import User
from tornado import gen
from tornado.gen import coroutine, Return
from tornado.testing import gen_test, AsyncHTTPTestCase
from mock import patch
import json
from apps.core.httpclient import (RESTfulAsyncClient,
                                  SessionClient)
from tornado.httpclient import (HTTPResponse)
from tornado.concurrent import TracebackFuture
from cStringIO import StringIO
from apps.auth.views import UserAuthBaseHandle
from apps.core.models.encoder import SQLAlchemy2DictEncoder
from sqlalchemy.orm.query import Query
from datetime import datetime


class UserModelTest(BaseTestCase):

    def test_user(self):
        self.assertEqual(User.query(User.id).count(), 0)

    @gen_test
    def test_create(self):
        self.assertEqual(User.query(User.id).count(), 0)
        user = User(
            username="test",
            tenant_id="mt_tenant_1",
            user_id="mt_user_1",)
        user.save_object()
        self.assertEqual(User.query(User).count(), 1)
        first_user = User.query(User).one()
        self.assertEqual(first_user.username, "test")
        self.assertEqual(first_user.tenant_id, "mt_tenant_1")
        self.assertEqual(first_user.user_id, "mt_user_1")
        yield gen.sleep(1)
        first_user.username = 'newtest'
        # first_user.updated_at = datetime(2010, 1, 1,tzinfo=UTC)
        first_user.save_object()
        self.assertEqual(User.query(User).count(), 1)
        first_user = User.query(User).one()
        self.assertGreater(first_user.updated_at,
                           first_user.created_at)
        # first_user.updated_at = datetime(2010, 1, 1, tzinfo=UTC)
        # first_user.save_object()
        first_user = User.query(User).first()
        # 一脸懵逼，这个单元测试怎么挂了。。。
        # self.assertEqual(first_user.updated_at.tzinfo.tzname(
        #     None), options.tz.tzname(None))

    def test_create_or_get(self):
        self.assertEqual(User.query(User.id).count(), 0)
        obj, is_created = User.create_or_get(username="test",
                                             tenant_id="mt_tenant_1",
                                             user_id="mt_user_1")
        self.assertEqual(obj.id, 1)
        self.assertEqual(is_created, True)

        obj, is_created = User.create_or_get(username="test",
                                             tenant_id="mt_tenant_1",
                                             user_id="mt_user_1")
        self.assertEqual(obj.id, 1)
        self.assertEqual(is_created, False)

        obj, is_created = User.create_or_get(username="test",
                                             tenant_id="mt_tenant_1",
                                             user_id="mt_user_1")
        self.assertEqual(obj.id, 1)
        self.assertEqual(is_created, False)

    def test_update_or_create(self):
        self.assertEqual(User.query(User.id).count(), 0)
        obj, is_created = User.update_or_create(
            username="test",
            defaults={"tenant_id": "mt_tenant_1",
                      "user_id": "mt_user_1"})
        self.assertEqual(obj.id, 1)
        self.assertEqual(is_created, True)
        self.assertEqual(User.query(User.id).count(), 1)

        first_user = User.query(User).one()
        self.assertEqual(first_user.username, "test")
        self.assertEqual(first_user.tenant_id, "mt_tenant_1")
        self.assertEqual(first_user.user_id, "mt_user_1")
        # 一样的数据则不修改
        obj, is_created = User.update_or_create(
            username="test",
            defaults={"tenant_id": "mt_tenant_1",
                      "user_id": "mt_user_1"})
        self.assertEqual(obj.id, 1)
        self.assertEqual(is_created, False)
        self.assertEqual(User.query(User.id).count(), 1)

        obj, is_created = User.update_or_create(
            username="test",
            defaults={"tenant_id": "mt_tenant_12",
                      "user_id": "mt_user_12"})
        self.assertEqual(obj.id, 1)
        self.assertEqual(is_created, False)
        self.assertEqual(User.query(User.id).count(), 1)
        first_user = User.query(User).first()
        self.assertEqual(first_user.username, "test")
        self.assertEqual(first_user.tenant_id, "mt_tenant_12")
        self.assertEqual(first_user.user_id, "mt_user_12")

    def test_todict(self):
        user = User(
            username="test",
            tenant_id="mt_tenant_1",
            user_id="mt_user_1",)
        user.save_object()
        self.assertEqual(User.query(User).count(), 1)
        first_user = User.query(User).one()
        self.assertIsNone(first_user.deleted_at)
        expect = {'username': u'test',
                  'user_id': u'mt_user_1',
                  'tenant_id': u'mt_tenant_1',
                  u'deleted_at': None,
                  'id': 1}
        user_obj = first_user.to_dict()
        for key, value in expect.iteritems():
            self.assertEqual(user_obj[key], value)

    def test_searchable(self):
        column = User.get_column_def("username")
        self.assertEqual(User.is_searchable(column, False), True)

    def test_getattr(self):
        user = User(
            username="test",
            tenant_id="mt_tenant_1",
            user_id="mt_user_1",)
        user.save_object()
        self.assertEqual(User.query(User).count(), 1)
        first_user = User.query(User).one()
        self.assertEqual(first_user['username'], "test")
        first_user['username'] = "test2"
        self.assertEqual(first_user.username, "test2")
        User.save_updates(first_user)

    def test_iter(self):
        user = User(
            username="test",
            tenant_id="mt_tenant_1",
            user_id="mt_user_1",)
        user.save_object()
        for i, value in user:
            pass
        obj = user.items()
        keys = user.keys()
        values = user.values()
        self.assertEqual(keys, [o[0] for o in obj])
        self.assertEqual(values, [o[1] for o in obj])

    def test_picker(self):
        User(
            username="test",
            tenant_id="mt_tenant_1",
            user_id="mt_user_1").save_object()
        user = User.query().first()
        # have not error
        dumped_user = user.dumps()
        loaded_user = User.loads(dumped_user)
        self.assertEqual(loaded_user.username, user.username)
        self.assertEqual(loaded_user.tenant_id, user.tenant_id)
        self.assertEqual(loaded_user.user_id, user.user_id)
        self.assertEqual(loaded_user.id, user.id)
        self.assertEqual(loaded_user.updated_at, user.updated_at)


class SSOTestCase(BaseTestCase, AsyncHTTPTestCase):
    contexts = None

    def get_app(self):
        from main import make_app
        return make_app()

    def setUp(self):  # mock外部调用函数
        if self.contexts is None:
            self.contexts = []

        def mock_fetch(request,
                       callback=None,
                       raise_error=True,
                       **kwargs):
            """mock 掉RESTfulAsyncClient的fetch函数，使之不再发起向外请求
            并且响应始终是固定的
            """
            future = TracebackFuture()
            if callback is not None:
                def handle_future(future):
                    """future的回调，单元测试里一般会挂上self.top"""
                    response = future.result()
                    self.io_loop.add_callback(callback, response)
                future.add_done_callback(handle_future)

            def immediately_done():
                """立即完成future"""
                buf = StringIO()
                buf.write(json.dumps({  # 思索。。这里好像只能写死，要传参的话得在_request上再打一层
                    "ok": True,
                    "mock": True,
                    'user': {
                        "id": "1",
                        "username": "testusername",
                    }
                }))
                response = HTTPResponse(request, 200, buffer=buf)
                future.set_result(response)
            self.io_loop.add_callback(immediately_done)
            return future
        # mock 掉RESTfulAsyncClient的fetch函数，使之不再发起向外请求
        o = patch.object(RESTfulAsyncClient, 'fetch',
                         side_effect=mock_fetch)
        self.contexts.append(o)
        super(SSOTestCase, self).setUp()

    @gen_test
    def test_patch(self):
        """测试patch：账号登录过程"""
        client = RESTfulAsyncClient(io_loop=self.io_loop)
        response = yield client.get("/some/path")
        self.assertEqual(response.code, 200)
        response = json.loads(response.body)
        # 这就已经是mock后的请求了。。哈哈哈哈
        self.assertItemsEqual(response, {
            "ok": True,
            "mock": True,
            'user': {
                "id": "1",
                "username": "testusername",
            }
        })

    def test_patch_with_callback(self):
        """测试patch：账号登录过程,带回调
        带回调时，不需要gen_test装饰器
        """
        client = RESTfulAsyncClient(io_loop=self.io_loop)
        client.get("/some/path",
                   callback=self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)

    def test_sso(self):
        """测试SSO过程
        默认的http_client是AsyncHTTPClient
        这里不用SessionClient，是因为SessionClient依赖RESTfulAsyncClient
        而后者被上面mock掉了
        """
        # 首页现在重定向到analyze了也需要登录了
        # response = self.fetch("/")
        # # 维持一个session
        # self.assertTrue(response.effective_url.startswith("http://localhost"))
        cookies = []
        # for cookie in response.headers.get_list("Set-Cookie"):
        #     cookies.append(self._parse_cookie(cookie))
        headers = {}
        url = self.reverse_url("user:logout")
        response = self.fetch(url, headers=headers)
        self.assertFalse(response.effective_url.startswith("http://localhost"))

        self.assertEqual(User.query(User.id).count(), 0)

        # 经过一番重定向(外部忽略)后,带着token回到callback页面，并登陆
        response2 = self.fetch("/user/callback",
                               method="POST",
                               body="token=suibianshenme",
                               headers=headers,
                               # !!!跟随重定向的时候，cookie就没了，这尼玛心塞
                               follow_redirects=False)
        self.assertEqual(User.query(User.id).count(), 1)
        first_user = User.query(User).one()
        self.assertEqual(first_user.username, "testusername")
        self.assertEqual(first_user.tenant_id, "mt_tenant_1")
        self.assertEqual(first_user.user_id, "mt_user_1")
        # 再次带着登陆的Cookie
        for cookie in response2.headers.get_list("Set-Cookie"):
            cookies.append(self._parse_cookie(cookie))
        headers = {"Cookie": "; ".join(cookies)}
        # 再访问之前需要登录的链接
        response = self.fetch("/analyze/",
                              headers=headers)
        self.assertTrue(response.effective_url.startswith(
            "http://localhost"))


class LoginTestCase(BaseTestCase, AsyncHTTPTestCase):
    contexts = None

    def get_app(self):
        from main import make_app
        return make_app()

    def get_http_client(self):
        return SessionClient(io_loop=self.io_loop)

    def get_user(self):
        user = User.query().filter_by(username="test").one()
        return user

    def setUp(self):  # mock需要登录的基类函数，统一返回测试用户
        if self.contexts is None:
            self.contexts = []
        super(LoginTestCase, self).setUp()
        user = User(
            username="test",
            tenant_id="mt_tenant_1",
            user_id="mt_user_1",)
        user.save_object()
        user_id = user.id

        def get_current_user():
            raise NotImplementedError("这个方法不应该被调用，参考get_current_user_async方法")
            # return User.query().get(user_id)  # bind session
        o = patch.object(UserAuthBaseHandle, 'get_current_user',
                         side_effect=get_current_user)

        @coroutine
        def get_current_user_async():
            user = User.query().get(user_id)
            raise Return(user)
        o = patch.object(UserAuthBaseHandle, 'get_current_user_async',
                         side_effect=get_current_user_async)
        self.contexts.append(o)
        o.__enter__()

    def _test_view_need_login(self):
        response = self.fetch("/star/dashboard/1")
        self.assertEqual(response.code, 200)


class JSONEncoderTestcase(LoginTestCase):

    def test_encode_query(self):
        self.assertEqual(User.query(User).count(), 1)
        query = User.query()
        self.assertIsInstance(query, Query)
        result = SQLAlchemy2DictEncoder(fields=['id',  # int
                                                'username',  # str
                                                'created_at']).encode(query)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        obj = result[0]
        self.assertEqual(obj['id'], 1)
        self.assertEqual(obj['username'], 'test')
        self.assertIsInstance(obj['created_at'], datetime)

    def test_encode_obj(self):
        self.assertEqual(User.query(User).count(), 1)
        first_user = User.query().first()
        obj = SQLAlchemy2DictEncoder(fields=['id',  # int
                                             'username',  # str
                                             'created_at']).encode(first_user)
        self.assertIsInstance(obj, dict)
        self.assertEqual(obj['id'], 1)
        self.assertEqual(obj['username'], 'test')
        self.assertIsInstance(obj['created_at'], datetime)
