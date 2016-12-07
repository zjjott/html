# coding=utf-8
from __future__ import unicode_literals
import sys
from IPython import start_ipython
import argparse
from apps.core.models.client import Client
import apps.conf  # flake8: noqa
from tornado.options import options
import subprocess


class BaseManage(object):
    name = None  # 启动子命令
    doc = ""  # 会用这个属性作为子命令文档

    def __init__(self, subparsers):
        self.parser = subparsers.add_parser(self.name, help=self.doc)
        self.add_arguments()
        self.parser.set_defaults(func=self.start)

    def add_arguments(self):
        """写一些启动参数或者不写"""
        pass

    def add_argument(self, *args, **kwargs):
        self.parser.add_argument(*args, **kwargs)

    def start(self, args):
        raise NotImplementedError(
            "manage need implement start func to start command")


class ShellManage(BaseManage):
    name = "shell"
    doc = "ipython shell with tornado env"

    def add_arguments(self):
        """写一些启动参数或者不写"""
        self.add_argument('params', nargs=argparse.REMAINDER,
                          help='other params to ipython')

    def start(self, args):
        sys.exit(start_ipython(args.params))


class DBShellManage(BaseManage):
    name = "dbshell"
    doc = "database shell client"

    def add_arguments(self):
        """写一些启动参数或者不写"""
        self.add_argument('params', nargs=argparse.REMAINDER,
                          help='other params to subprocess')

    def start(self, args):
        Client.runshell(args.params)


class RedisManage(BaseManage):
    name = "redis"
    doc = "start redis-cli"

    def start(self, args):
        args = ['redis-cli']
        redis_options = options.cache_options
        if "host" in redis_options:
            args.append("-h")
            args.append("%s" % redis_options['host'])
        if "port" in redis_options:
            args.append("-p")
            args.append("%s" % redis_options['port'])
        if "selected_db" in redis_options:
            args.append("-n")
            args.append("%s" % redis_options['selected_db'])
        subprocess.call(args)


managers = [ShellManage, DBShellManage,  # flake8: noqa
            RedisManage,
            ]
