# coding=utf-8
from __future__ import unicode_literals
import sys
from IPython import start_ipython
import argparse
from apps.core.models.client import Client
from tornado.util import import_object
import apps.conf  # flake8: noqa
from tornado.options import options
import subprocess
from library.ec2utils import Ec2Signer
from datetime import datetime
from apps.core.datastruct import QueryDict


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


class AdminManage(BaseManage):
    name = "admin"
    doc = "start admin manage web"

    def add_arguments(self):
        """写一些启动参数或者不写"""
        self.add_argument('--port',
                          type=int,
                          help='admin web manage port', dest="port")
        self.add_argument('--host',
                          help='admin web manage host', dest="host")
        self.add_argument('--debug',
                          action="store_true",
                          default=options.debug,
                          help='admin web manage host', dest="debug")

    def start(self, args):
        admin = import_object("apps.admin.app")
        admin.run(args.host, args.port, debug=args.debug)


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


class SignerManage(BaseManage):
    name = "generate-sign"
    doc = "generate ec2 sign used by curl"

    def add_arguments(self):
        self.add_argument('--access',
                          '-k',
                          help='ec2 AWSAccessKeyId', dest="access")
        self.add_argument('--secret', '-s',
                          help='ec2 AWSAccessSecert', dest="secret")
        self.add_argument('--action', '-a',
                          help='ec2 Action', dest="action")
        self.add_argument('--verb', '-m',
                          default="GET",
                          choices=["GET", "POST"],
                          help='ec2 Method', dest="verb")
        self.add_argument('--path', '-p',
                          help='ec2 path', dest="path")
        self.add_argument('--host',
                          help='ec2 host', dest="host")
        self.add_argument('--version', '-v',
                          default="2",
                          help='ec2 SignatureVersion', dest="version")
        self.add_argument('--method',
                          default="HmacSHA256",
                          choices=["HmacSHA256", "HmacSHA1"],
                          help='ec2 SignatureMethod', dest="method")

    def start(self, args):
        AWSAccessKeyId = args.access
        signer = Ec2Signer(args.secret)
        params = {
            "Action": args.action,
            "AWSAccessKeyId": AWSAccessKeyId,
            "Timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "SignatureVersion": args.version,
            "SignatureMethod": args.method,
        }
        d = {
            'access': AWSAccessKeyId,
            'host': args.host,
            'verb': args.verb,
            'path': args.path,
            'params': params,
        }
        Signature = signer.generate(d)
        params['Signature'] = Signature
        if args.verb == "GET":
            query = QueryDict(params)
            print "curl -v http://%s%s?%s" % (args.host,
                                              args.path,
                                              query.urlencode())
        else:
            body = ["-F %s=%s" % (key, value)
                    for key, value in params.iteritems()]
            query = " ".join(body)
            print "curl -v %s http://%s%s" % (query,
                                              args.host,
                                              args.path)

managers = [ShellManage, DBShellManage,  # flake8: noqa
            AdminManage, RedisManage,
            SignerManage]
