# coding=utf-8
from __future__ import unicode_literals
from tornado.options import define, parse_config_file, options
from tornado.log import enable_pretty_logging
import logging
from pytz import timezone
import site
from os.path import dirname, join
from library.utils.encoding import ensure_utf8
application_path = dirname(__file__)
site.addsitedir(ensure_utf8(join(application_path,
                                 "thirdpart")))
define("debug", default=True)
define("testing", default=False)


define("secret")
define("session_cookie_age", type=int, default=3)  # 3天session过期
define("session_engine", default="apps.core.session.cookie.CookieSessionStore")


define("port", type=int, help="listen at port")
define("test_db", default="sqlite:///", help="test db uri")
define("db_pool_size",
       type=int,
       default=20,
       help="connection pool size")

define("sql_connection", help="master uri of databases")
define("tz", default=timezone("Asia/Shanghai"),
       help="timezone")  # +8:06:00


define("cache_time", type=int, default=300)  # 300秒默认cache过期
define("cache_engine", default="apps.core.cache.memory.MemoryCache")
define("cache_options", default=dict())

define("process_num", default=0)  # 0即CPU个数
define("broker_transport", default="redis")
define("broker_url", default="redis://127.0.0.1:6379/0")
define("celery_result_backend", default="redis://127.0.0.1:6379/0")
define("celery_task_result_expires", type=int, default=1800)
define("celery_max_cached_results", type=int, default=300)
define("celery_timezone", default='Asia/Shanghai')
define("celeryd_concurrency", type=int, default=6)
define("celery_accept_content", type=list, default=['pickle',
                                                    'json',
                                                    'msgpack', 'yaml'])


parse_config_file("conf/app.conf")


class LogOption(dict):

    def __missing__(self, key):
        return dict.get(self, key)

    def __getattr__(self, key):
        return self.get(key)

    def __setattr__(self, key, value):
        if key in self:
            self[key] = value
        else:
            return super(LogOption, self).__setattr__(key)
LOGGING = {
    "logger": {
        "tornado.access": {  # accesslog
            "logging": "INFO",
            "log_rotate_mode": "time",
            "log_file_prefix": "logs/access.log",
            "log_rotate_when": "W5",
            "log_rotate_interval": 1,
            "log_file_num_backups": 10,
        },
        "tornado.application": {  # exception log/application
            "logging": "INFO",
            "log_rotate_mode": "time",
            "log_file_prefix": "logs/application.log",
            "log_rotate_when": "W5",
            "log_rotate_interval": 1,
            "log_file_num_backups": 10,
        },
        "tornado.general": {  # http exception warning log/general
            "logging": "INFO",
            "log_rotate_mode": "time",
            "log_file_prefix": "logs/general.log",
            "log_rotate_when": "W5",
            "log_rotate_interval": 1,
            "log_file_num_backups": 10,
        },
    }
}
if options.debug:  # 只在debug模式开sql日志
    LOGGING['logger']["sqlalchemy"] = {
        "logging": "INFO",
        "log_rotate_mode": "time",
        "log_file_prefix": "logs/db.log",
        "log_rotate_when": "W5",
        "log_rotate_interval": 1,
        "log_file_num_backups": 10,
    }
for name, logoptions in LOGGING['logger'].iteritems():
    option = LogOption(**logoptions)
    enable_pretty_logging(option, logging.getLogger(name))
