# coding=utf-8
from __future__ import unicode_literals
from tornado.testing import AsyncTestCase
from apps.core.models import (ModelBase,
                              _get_master_engine,
                              _get_slave_engine)
from tornado.options import options
from apps.core.urlutils import urlpattens
from apps.auth.views import LoginHandler
from apps.views import IndexHandler
from apps.core.datastruct import QueryDict, lru_cache
from simplejson import loads
from tornado.testing import AsyncHTTPTestCase, gen_test
from apps.core.httpclient import (RESTfulAsyncClient, SessionClient)
from apps.core.crypto import get_random_string
from tornado.web import URLSpec
import re
from tornado.web import Application
from apps.core.cache.base import CacheBase, cache as cache_proxy
from tornado.gen import sleep
from mock import patch
from apps.core.timezone import now
from concurrent.futures import ThreadPoolExecutor
import thread
# 这样不会清掉数据库哈
options.testing = True  # 这个太关键了所以不用mock，下边的base_url改掉了


class EngineTest(AsyncTestCase):
    """测试是否已经是测试用的sql连接了"""
    contexts = None

    def setUp(self):
        if self.contexts is None:
            self.contexts = []
        o = patch.object(options.mockable(), 'sql_connection',
                         b"sqlite:///")
        self.contexts.append(o)
        for context in self.contexts:
            context.__enter__()
        super(EngineTest, self).setUp()
        engine = _get_master_engine()
        self.assertEqual(str(engine.url), options.test_db)
        self.assertEqual(engine.driver, "pysqlite")
        engine = _get_slave_engine()
        self.assertEqual(str(engine.url), options.test_db)
        self.assertEqual(engine.driver, "pysqlite")

    def tearDown(self):
        engine = _get_master_engine()
        self.assertEqual(str(engine.url), options.test_db)
        self.assertEqual(engine.driver, "pysqlite")
        engine = _get_slave_engine()
        self.assertEqual(str(engine.url), options.test_db)
        self.assertEqual(engine.driver, "pysqlite")

        for context in self.contexts:
            context.__exit__()
        super(EngineTest, self).tearDown()

    def test_engine(self):
        engine = _get_master_engine()
        self.assertEqual(str(engine.url), options.test_db)
        self.assertEqual(engine.driver, "pysqlite")
        engine = _get_slave_engine()
        self.assertEqual(str(engine.url), options.test_db)
        self.assertEqual(engine.driver, "pysqlite")


class BaseTestCase(EngineTest):
    contexts = None

    @staticmethod
    def _parse_cookie(cookie_line):
        return cookie_line.split(";")[0]

    def reverse_url(self, url_name, *args):
        return self.get_url(self._app.reverse_url(url_name, *args))

    def setUp(self):
        if self.contexts is None:
            self.contexts = []
        o = patch.object(options.mockable(), 'base_url',
                         b"/")
        self.contexts.append(o)
        super(BaseTestCase, self).setUp()

        engine = _get_master_engine()
        self.assertEqual(engine.driver, "pysqlite")
        ModelBase.metadata.create_all(engine)

    def tearDown(self):
        # 用sqlite 内存数据库不需要删除,主要是为了本地文件而搞的
        engine = _get_master_engine()
        self.assertEqual(str(engine.url), options.test_db)
        self.assertEqual(engine.driver, "pysqlite")
        engine = _get_slave_engine()
        self.assertEqual(str(engine.url), options.test_db)
        self.assertEqual(engine.driver, "pysqlite")
        ModelBase.metadata.drop_all(engine)

        super(BaseTestCase, self).tearDown()


class UrlTestCase(BaseTestCase, AsyncHTTPTestCase):

    def get_app(self):
        url = urlpattens('test',
                         [
                             ("/login/", LoginHandler, None, "login"),
                             ("/callback", LoginHandler, None, "callback"),
                         ]
                         )
        return Application(url)

    def test_reverse(self):
        self.assertEqual(self._app.reverse_url("test:login"), "/test/login/")

    def test_urlpatten_with_prefex(self):
        url = urlpattens('user',
                         [
                             ("/login/", LoginHandler),
                             ("/callback", LoginHandler),
                         ]
                         )
        root_url = [(r"/", IndexHandler)]
        new_urls = root_url + url
        self.assertEqual(new_urls[2].regex,
                         re.compile(r"/user/callback$"))

    def test_urlpatten_without_prefex(self):
        url = urlpattens('',
                         [
                             ("/login/", LoginHandler),
                             ("/callback", LoginHandler),
                         ]
                         )
        root_url = [(r"/", IndexHandler)]
        new_urls = root_url + url
        self.assertEqual(new_urls[1].regex,
                         URLSpec(r"/login/", LoginHandler).regex)

    def test_urlpatten_radd(self):
        url = urlpattens('',
                         [
                             ("/login/", LoginHandler),
                             ("/callback", LoginHandler),
                         ]
                         )
        root_url = [(r"/", IndexHandler)]
        new_urls = url + root_url  # 换顺序
        self.assertEqual(new_urls[0].regex,
                         URLSpec(r"/login/", LoginHandler).regex)


class DataStructTestCase(EngineTest):

    def test_urlencode_safe(self):
        q = QueryDict({})
        q['next'] = '/a&b/'
        self.assertEqual(q.urlencode(), 'next=%2Fa%26b%2F')
        self.assertEqual(q.urlencode("/"), 'next=/a%26b/')

    def test_urlencode_unicode(self):
        q = QueryDict({})
        q['next'] = '啊'
        self.assertEqual(q.urlencode(), 'next=%E5%95%8A')

    def test_urlencode_list(self):
        q = QueryDict({})
        q['next'] = ['1', "2"]
        self.assertEqual(q.urlencode(), 'next=1&next=2')

    def test_lru(self):
        store = dict(zip("abcd", range(4)))

        @lru_cache(2)
        def somefunc(arg):
            return store[arg]

        self.assertEqual(somefunc("a"), 0)
        self.assertEqual(somefunc("b"), 1)
        cache_info = somefunc.cache_info()
        self.assertEqual(cache_info.misses, 2)
        self.assertEqual(cache_info.hits, 0)

        self.assertEqual(somefunc("a"), 0)
        self.assertEqual(somefunc("b"), 1)

        cache_info = somefunc.cache_info()
        self.assertEqual(cache_info.misses, 2)
        self.assertEqual(cache_info.hits, 2)

        somefunc.cache_clear()
        self.assertEqual(somefunc("a"), 0)
        self.assertEqual(somefunc("b"), 1)
        cache_info = somefunc.cache_info()
        self.assertEqual(cache_info.misses, 2)
        self.assertEqual(cache_info.hits, 0)

        self.assertEqual(somefunc("c"), 2)
        self.assertEqual(somefunc("d"), 3)
        cache_info = somefunc.cache_info()
        self.assertEqual(cache_info.misses, 4)
        self.assertEqual(cache_info.hits, 0)

    def test_lru_nosize(self):
        store = dict(zip("abcd", range(4)))

        @lru_cache(None)
        def somefunc(arg):
            return store[arg]
        self.assertEqual(somefunc("a"), 0)
        self.assertEqual(somefunc("b"), 1)
        cache_info = somefunc.cache_info()
        self.assertEqual(cache_info.misses, 2)
        self.assertEqual(cache_info.hits, 0)


class ClientTestCase(BaseTestCase, AsyncHTTPTestCase):

    def get_app(self):
        from main import make_app
        return make_app()

    def test_get(self):
        client = RESTfulAsyncClient()
        url = self.get_url("/api/")
        client.get(url,
                   {"a": "b", "c": 1},
                   callback=self.stop)
        response = self.wait()
        response = loads(response.body)["data"]
        self.assertItemsEqual(response['query'], {
            "a": "b",
            "c": "1"
        })

    def test_post(self):
        client = RESTfulAsyncClient()
        url = self.get_url("/api/")
        response = client.post(url,
                               {"a": "b", "c": ["1", 3, 4]},
                               callback=self.stop)
        # self.assertEqual()
        response = self.wait()
        response = loads(response.body)["data"]
        self.assertItemsEqual(response['form'], {
            "a": "b",
            "c": ["1", 3, 4]
        })

    def test_put(self):
        client = RESTfulAsyncClient()
        url = self.get_url("/api/")
        response = client.put(url,
                              {"a": "b", "c": ["1", 3, 4]},
                              callback=self.stop)
        response = self.wait()
        response = loads(response.body)["data"]
        self.assertItemsEqual(response['form'], {
            "a": "b",
            "c": ["1", 3, 4]
        })

    def test_delete(self):
        client = RESTfulAsyncClient()
        url = self.get_url("/api/")
        response = client.delete(url,
                                 callback=self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)


class TestCrypto(EngineTest):

    def test_random(self):
        self.assertEqual(len(get_random_string(12)), 12)
        self.assertEqual(len(get_random_string(20)), 20)
        self.assertNotEqual(get_random_string(12), get_random_string(12))


class TestTimeUtils(EngineTest):

    def test_now(self):
        dt = now()
        self.assertIsNotNone(dt.tzinfo)


class TestSessionClient(AsyncHTTPTestCase, BaseTestCase):

    def get_app(self):
        from main import make_app
        return make_app()

    def get_http_client(self):
        return SessionClient(io_loop=self.io_loop)

    def test_single_instance(self):
        new_client = SessionClient(io_loop=self.io_loop)
        self.assertEqual(id(new_client), id(self.http_client))
        self.assertEqual(id(new_client.cookiejar),
                         id(self.http_client.cookiejar))

    def test_session(self):
        url = self.get_url("/api/")
        self.http_client.get(url, callback=self.stop)
        response = self.wait()
        # 第一次请求有Set-Cookie头
        self.assertEquals(response.code, 200)
        self.assertIn("Set-Cookie", response.headers)
        url = self.get_url("/api/")
        self.http_client.get(url, callback=self.stop)
        response = self.wait()
        # 第二次响应头就没有Set-Cookie了
        self.assertNotIn("Set-Cookie", response.headers)
        self.assertIn("cookie", response.request.headers)
        # 外部请求影响速度，不测了
        # self.http_client.get("http://httpbin.org/get",
        #                      callback=self.stop)
        # response = self.wait()
        # self.assertNotIn("cookie", response.request.headers)


class MemoryCacheTestCase(EngineTest):
    contexts = None

    def setUp(self):
        if self.contexts is None:
            self.contexts = []
        o = patch.object(options.mockable(), 'cache_engine',
                         "apps.core.cache.memory.MemoryCache")
        self.contexts.append(o)
        super(MemoryCacheTestCase, self).setUp()

    @gen_test
    def test_get(self):
        CacheBase.configure(
            "apps.core.cache.memory.MemoryCache", io_loop=self.io_loop)
        cache = CacheBase(self.io_loop)
        value = yield cache.get("key_not_exist")
        self.assertEqual(value, None)

    @gen_test
    def test_set(self):
        CacheBase.configure(
            "apps.core.cache.memory.MemoryCache", io_loop=self.io_loop)
        cache = CacheBase(self.io_loop)
        yield cache.set("somekey", 1)
        value = yield cache.get("somekey")
        self.assertEqual(value, 1)

    @gen_test
    def test_size_set(self):
        CacheBase.configure(
            "apps.core.cache.memory.MemoryCache", io_loop=self.io_loop,
            defaults={"max_size": 2})
        cache = CacheBase()
        yield cache.set("somekey", 1)
        yield cache.set("somekey2", 2)
        yield cache.set("somekey3", 3)
        value = yield cache.get("somekey")
        self.assertEqual(value, None)

    @gen_test
    def test_size_lru(self):
        CacheBase.configure(
            "apps.core.cache.memory.MemoryCache", io_loop=self.io_loop,
            defaults={"max_size": 2})
        cache = CacheBase()
        yield cache.set("somekey", 1)
        yield cache.set("somekey2", 2)
        # yield cache.set("somekey3", 3)

        value = yield cache.get("somekey")
        self.assertEqual(value, 1)

        yield cache.set("somekey3", 3)  # somekey2被挤出

        value = yield cache.get("somekey")
        self.assertEqual(value, 1)

        value = yield cache.get("somekey2")
        self.assertEqual(value, None)

    @gen_test
    def test_timeout(self):
        CacheBase.configure(
            "apps.core.cache.memory.MemoryCache", io_loop=self.io_loop,
            defaults={"max_size": 2})
        cache = CacheBase()
        yield cache.set("somekey", 1, 1)
        yield cache.set("somekey2", 2, 2)
        yield sleep(2)

        self.assertNotIn("somekey", cache._cache)
        self.assertNotIn("somekey", cache)

    @gen_test
    def test_proxy(self):
        o = patch.object(options.mockable(),
                         'cache_options',
                         {"max_size": 2})
        o.__enter__()
        self.contexts.append(o)
        o = patch.object(options.mockable(),
                         'cache_engine',
                         "apps.core.cache.memory.MemoryCache")
        o.__enter__()
        self.contexts.append(o)
        yield cache_proxy.set("somekey", 1, 1)
        yield cache_proxy.set("somekey2", 2, 2)
        yield sleep(2)
        self.assertNotIn("somekey", cache_proxy._cache)
        self.assertNotIn("somekey", cache_proxy)


class A(object):

    def __init__(self, arg):
        self.arg = arg


class RedisCacheTest(BaseTestCase):
    # teardown怎么清掉呢。。。。

    @gen_test
    def test_get(self):
        CacheBase.configure("apps.core.cache.redis.RedisCache",
                            defaults=options.cache_options)
        cache = CacheBase(self.io_loop)
        value = yield cache.get("key_not_exist")
        self.assertEqual(value, None)

    @gen_test
    def test_set(self):
        CacheBase.configure("apps.core.cache.redis.RedisCache",
                            defaults=options.cache_options)
        cache = CacheBase(self.io_loop)
        yield cache.set("testkey", "value")
        value = yield cache.get("testkey",)
        self.assertEqual(value, "value")
        yield cache.delete("testkey")
        value = yield cache.get("testkey",)
        self.assertEqual(value, None)

    @gen_test
    def test_set_object(self):
        CacheBase.configure("apps.core.cache.redis.RedisCache",
                            defaults=options.cache_options)
        cache = CacheBase(self.io_loop)

        obj = A(123123)
        yield cache.set("testkey", obj)
        value = yield cache.get("testkey",)
        self.assertEqual(isinstance(value, A), True)
        self.assertEqual(value.arg, 123123)
        yield cache.delete("testkey")
        value = yield cache.get("testkey",)
        self.assertEqual(value, None)

    @gen_test
    def test_set_dict(self):
        CacheBase.configure("apps.core.cache.redis.RedisCache",
                            defaults=options.cache_options)
        cache = CacheBase(self.io_loop)

        obj = {"asd": 123, "zxc": "qwe"}
        yield cache.set("testkey", obj)
        value = yield cache.get("testkey",)
        self.assertEqual(isinstance(value, dict), True)
        self.assertItemsEqual(value, {"asd": 123, "zxc": "qwe"})
        yield cache.delete("testkey")
        value = yield cache.get("testkey",)
        self.assertEqual(value, None)

    @gen_test
    def test_bin(self):
        CacheBase.configure("apps.core.cache.redis.RedisCache",
                            defaults=options.cache_options)
        cache = CacheBase(self.io_loop)

        obj = {"asd": 123, "zxc": u"啊"}
        yield cache.set("testkey", obj)

        value = yield cache.get("testkey",)
        self.assertItemsEqual(value, {"asd": 123, "zxc": u"啊"})
        self.assertTrue(isinstance(value["zxc"], unicode))

        obj = {"asd": 123, "zxc": b"\x00\x01\x02"}
        yield cache.set("testkey2", obj)

        value = yield cache.get("testkey2",)
        self.assertTrue(isinstance(value["zxc"], bytes))
        self.assertEquals(value["zxc"], b"\x00\x01\x02")


class ExecutorTestCase(EngineTest):

    def user_pow(self, *args):
        self.assertNotEqual(thread.get_ident(), self.father_id)
        return pow(*args)

    def test_thread_db(self):
        self.father_id = thread.get_ident()
        with ThreadPoolExecutor(max_workers=4) as exectors:
            future = exectors.map(self.user_pow, range(5), range(5))
            self.assertItemsEqual(list(future), [1, 1, 4, 27, 256])
