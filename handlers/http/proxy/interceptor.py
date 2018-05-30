# -*- coding: utf-8 -*-
# Created by restran on 2018/5/29
from __future__ import unicode_literals, absolute_import

import types
import imp
code = """
class Interceptor(object):
    def __init__(self, handler):
        self.handler = handler
    
    def on_request(self):
        print('on_request')

    def on_response(self, chunk):
        print('on_response')

    def on_finished(self):
        print('on_finished xxxxx')
"""

mod = types.ModuleType('abc')
code = compile(code, '<string>', 'exec')

mod.__package__ = ''
exec(code, mod.__dict__)
