# -*- coding: utf-8 -*-
# Created by restran on 2018/5/29
from __future__ import unicode_literals, absolute_import


class Interceptor(object):
    def __init__(self, handler):
        self.handler = handler

    def on_request(self, *args, **kwargs):
        pass

    def on_response(self, *args, **kwargs):
        pass

    def on_finished(self, *args, **kwargs):
        pass

