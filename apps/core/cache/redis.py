# coding=utf-8

from apps.core.cache.base import CacheBase, DEFAULT_TIMEOUT
from tornado.gen import Task, coroutine, Return
from pickle import loads, dumps

from library.redisclient import ReconnectClient


class RedisCache(CacheBase):

    @classmethod
    def configurable_base(cls):
        return RedisCache

    def initialize(self, io_loop, defaults=None):
        defaults = self.defaults if defaults is None else defaults
        connect_kwargs = {
            "host": defaults.get("host", "localhost"),
            "port": defaults.get("port", 6379),
            "db": defaults.get("db", 0),
        }
        client = ReconnectClient(io_loop)
        client.connect(**connect_kwargs
                       )
        self._cache = client
        super(RedisCache, self).initialize(io_loop, defaults)

    def __contains__(self, key):
        """不附带删除、提到最前的副作用"""
        key = self._make_key(key)
        return self._sync_cache.ttl(key) > 0

    def get_backend_timeout(self, timeout=DEFAULT_TIMEOUT):
        """
        Returns the timeout value usable by this backend based upon the provided
        timeout.
        """
        if timeout == DEFAULT_TIMEOUT:
            timeout = self.default_timeout
        elif timeout == 0:
            # ticket 21147 - avoid time.time() related precision issues
            timeout = -1

        return None if timeout is None else timeout

    @coroutine
    def get(self, key, default=None, version=None, callback=None):
        key = self._make_key(key, version)
        result = yield Task(self._cache.get, key)
        if result:
            raise Return(loads(result))
        else:
            raise Return(result)

    @coroutine
    def set(self, key, value,
            timeout=DEFAULT_TIMEOUT, version=None, callback=None):
        key = self._make_key(key, version)
        expired_time = self.get_backend_timeout(timeout)
        value = dumps(value)
        result = yield Task(self._cache.setex, key, expired_time, value)
        raise Return(result)

    @coroutine
    def delete(self, key, version=None):
        key = self._make_key(key, version)
        result = yield Task(self._cache.delete, key)
        raise Return(result)
