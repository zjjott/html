# coding=utf-8
from __future__ import unicode_literals
from apps.auth.views import (LoginHandler, LogoutHandler
                             ,CurrentHandler)
from apps.core.urlutils import urlpattens
routes = [
    (r"/", CurrentHandler),
    (r"/login/", LoginHandler),
    (r"/logout/", LogoutHandler, None, "logout"),

]

urls = urlpattens('user', routes)
