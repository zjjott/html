# coding=utf-8
from __future__ import unicode_literals, absolute_import
from tornado.util import Configurable
from collections import defaultdict
import weakref
from tornado.ioloop import IOLoop
import logging
from redis import from_url
from tornado.options import options
from library.redisclient import ReconnectClient
logger = logging.getLogger("tornado.general")


class CeleryBus(Configurable):
    """监听celeryev事件
    只支持redis吗= =
    """
    def __new__(cls, io_loop=None, force_instance=False, **kwargs):
        """单例"""
        io_loop = io_loop or IOLoop.current()
        if force_instance:
            instance_cache = None
        else:
            instance_cache = cls.cached_instances()
        if instance_cache is not None and io_loop in instance_cache:
            return instance_cache[io_loop]
        instance = super(CeleryBus, cls).__new__(cls, io_loop=io_loop,
                                                 **kwargs)
        # Make sure the instance knows which cache to remove itself from.
        # It can't simply call _async_clients() because we may be in
        # __new__(AsyncHTTPClient) but instance.__class__ may be
        # SimpleAsyncHTTPClient.
        instance._instance_cache = instance_cache
        if instance_cache is not None:
            instance_cache[instance.io_loop] = instance
        return instance

    @classmethod
    def configurable_base(cls):
        return CeleryBus

    @staticmethod
    def _get_tornado_redis(redis_url, ioloop, callback=None):
        redis_client = from_url(redis_url)
        connection_kwargs = redis_client.connection_pool.connection_kwargs
        client = ReconnectClient(ioloop)
        client.connect(connection_kwargs["host"],
                       connection_kwargs["port"],
                       connection_kwargs["db"],
                       callback=callback
                       )
        return client

    def initialize(self, io_loop, broker,
                   backend):
        # 看了下client的源代码，订阅发布模式下，client只能运行订阅发布命令
        # 因此需要两个客户端
        self.backend_redis = self._get_tornado_redis(
            backend, io_loop)
        self.backend_redis_ps = self._get_tornado_redis(
            backend, io_loop, self.start)
        self.io_loop = io_loop
        self.callbacks = defaultdict(set)
        # 上面的client有个回调会在连接redis后运行，因此start也稍后开始
        # io_loop.add_callback(self.start)

    def add_callback(self, task_name, callback):
        self.callbacks[task_name].add(callback)

    def on_message(self, message):
        # msg = self.decode(message)
        # self.io_loop.add_callback()
        print "on_message", message

    def on_close(self):
        if not hasattr(self, "sub"):
            logger.warning("subscriber not exist")
            return
        self.punsubscribe("celery-task-meta*", self)

    @classmethod
    def cached_instances(cls):
        attr_name = '_cached_instances' + cls.__name__
        if not hasattr(cls, attr_name):
            setattr(cls, attr_name, weakref.WeakKeyDictionary())
        return getattr(cls, attr_name)

    def start(self):
        """实际上会在单例 进行初始化的时候调用隔哈？"""
        logger.info("Subscriber redis:%r 'celeryev' start",
                    self.backend_redis)
        self.backend_redis_ps.psubscribe("celery-task-meta*", self.on_message)
        logger.info("Subscriber redis 'celeryev' hooked")

    @classmethod
    def configurable_default(cls):
        return cls

    @classmethod
    def ensure_start(cls):
        ioloop = IOLoop.current()
        instance = cls(ioloop,
                       broker=options.BROKER_URL,  # 消息代理
                       backend=options.CELERY_RESULT_BACKEND  # 结果存储
                       )
        return instance
