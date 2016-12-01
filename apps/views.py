# coding=utf-8
from __future__ import unicode_literals
from apps.core.views import BaseHandler
from apps.core.template import FileLoader
from tornado.gen import coroutine


class APIHandler(BaseHandler):
    """Ping/Pong视图"""
    @coroutine
    def get(self):
        arguments = self.request.query_arguments
        return self.json_respon({"headers":
                                 dict(self.request.headers),
                                 "query": arguments})

    @coroutine
    def post(self):
        arguments = self.request.query_arguments
        body_arguments = self.request.body_arguments
        return self.json_respon({"headers":
                                 dict(self.request.headers),
                                 "form": body_arguments,
                                 "query": arguments})

    @coroutine
    def put(self):
        arguments = self.request.query_arguments
        body_arguments = self.request.body_arguments
        return self.json_respon({"headers":
                                 dict(self.request.headers),
                                 "form": body_arguments,
                                 "query": arguments})

    @coroutine
    def delete(self):
        arguments = self.request.query_arguments
        body_arguments = self.request.body_arguments
        return self.json_respon({"headers":
                                 dict(self.request.headers),
                                 "form": body_arguments,
                                 "query": arguments})


class IndexHandler(BaseHandler):
    loader = FileLoader("templates/")  # tornado会缓存模板。。

    def get(self):
        return self.render("index.html")

    def post(self):
        raise ValueError("test error")
