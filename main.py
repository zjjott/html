# coding=utf-8
from __future__ import unicode_literals
import tornado.ioloop
from apps.views import IndexHandler, APIHandler
from apps.auth.urls import urls
from apps.taskapi.urls import urls as task_urls
import apps.conf  # noq
from tornado.options import options
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from apps.core import uimodules
from apps.core.template import FileLoader

settings = {
    "cookie_secret": options.secret,
    "login_url": "/user/login/",
    "static_path": "static/dest",
    "static_url_prefix": "/static/",
    "compress_response": True,
    "debug": options.debug,
    "ui_modules": uimodules,
    "template_loader": FileLoader("templates/")
}


def make_app():
    url1 = [
        (r"/", IndexHandler),
        (r"/api/", APIHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler,
         {"path": "static/dest"}),
    ]
    new_urls = url1 + urls + task_urls
    # print "make_app"
    return tornado.web.Application(new_urls,
                                   **settings)


if __name__ == '__main__':
    app = make_app()
    if options.debug:
        app.listen(options.port)
    else:
        # 生产环境 这样感觉有些不安😂要不要放在wsgi里面。。。ioloop怎么办。。
        server = HTTPServer(app)
        server.bind(options.port)
        server.start(options.process_num)
    IOLoop.current().start()
