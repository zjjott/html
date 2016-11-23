# coding=utf-8
from __future__ import unicode_literals
from apps.auth.views import (LoginHandler, LogoutHandler,
                             CallbackHandler)
from apps.core.urlutils import urlpattens
routes = [
    (r"/login/", LoginHandler),
    (r"/logout/", LogoutHandler, None, "logout"),
    (r"/callback", CallbackHandler),
]

urls = urlpattens('user', routes)
