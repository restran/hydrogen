# -*- coding: utf-8 -*-
# Created by restran on 2017/10/13
from __future__ import unicode_literals, absolute_import

import converter.api

url_handlers = [
    ('/api/converter/convert-data/', converter.api.convert_data, ['POST'])
]


def init_url_rules(app, url_map_list=url_handlers):
    for u in url_map_list:
        if len(u) > 2:
            methods = u[2]
        else:
            methods = None
        app.add_url_rule(rule=u[0], view_func=u[1], methods=methods)
