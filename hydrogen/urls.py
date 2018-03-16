# -*- coding: utf-8 -*-
# Created by restran on 2017/10/13
from __future__ import unicode_literals, absolute_import
from bottle import Bottle, Route
import converter.api
import crypto.api

url_handlers = [
    ('/api/converter/convert-data/', converter.api.convert_data, ['POST']),
    ('/api/converter/what-encode/', converter.api.what_encode, ['POST']),
    ('/api/crypto/decode-data/', crypto.api.decode_data, ['POST'])
]


def init_url_rules(app: Bottle, url_map_list=url_handlers):
    for u in url_map_list:
        if len(u) > 2:
            methods = u[2]
        else:
            methods = None

        app.route(path=u[0], method=methods, callback=u[1])
        # app.add_route(Route(app, rule=u[0], method=methods,  callback=u[1]))
