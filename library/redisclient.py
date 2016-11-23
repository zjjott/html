# coding=utf-8
from __future__ import unicode_literals
from toredis import Client


class ReconnectClient(Client):
    """重连
    """
    connect_kwargs = {}

    def connect(self,
                host='localhost',
                port=6379,
                db=0,
                callback=None,
                is_reload=False):
        # 记录连接参数用于下次重连
        # 没有保存的参数，或者is_reload为True，则更新
        should_update = (not self.connect_kwargs or is_reload)
        if not should_update:
            host = self.connect_kwargs.get("host", host)
            port = self.connect_kwargs.get("port", port)
            db = self.connect_kwargs.get("db", db)
            callback = self.connect_kwargs.get("callback", callback)

        def select_db():
            """连接后切换数据库"""
            self.select(db)
            if callback is not None:
                callback()
        if should_update:
            self.connect_kwargs.update(host=host,
                                       port=port,
                                       callback=callback)
        super(ReconnectClient, self).connect(host=host,
                                             port=port,
                                             callback=select_db)

    def on_disconnect(self):
        """
        close时所有已存在的回调函数都会以None被调用：cb(None)
        并且置为空
        然后才调用该方法
        """
        # connect_kwargs如果有callback参数会和self.connect的callback冲突
        #
        self._io_loop.call_later(1, self.connect,
                                 )


# class
