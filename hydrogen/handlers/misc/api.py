# -*- coding: utf-8 -*-
# Created by restran on 2017/10/13
from __future__ import unicode_literals, absolute_import

import logging
from base64 import b64encode

from mountains import text_type, force_bytes, force_text
from .utils import *
from utils import APIHandler

logger = logging.getLogger(__name__)


def smart_text(s):
    try:
        if isinstance(s, str) or isinstance(s, bytes):
            s = force_text(s)
        else:
            s = text_type(s)
    except:
        s = text_type(s)

    if isinstance(s, bytes):
        s = text_type(s)
    return s


def do_utility_handle(method, data, params, multiple_input):
    if method == 'ip2int':
        func = IPConverter.ip2int
    elif method == 'int2ip':
        func = IPConverter.int2ip
    elif method == 'remove_duplicated':
        func = remove_duplicated
    elif method == 'char_count':
        func = char_count
    elif method == 'caidao_decode':
        func = caidao_decode
    elif method == 'sort_asc':
        func = sort_asc
    elif method == 'sort_desc':
        func = sort_desc
    else:
        result = '!!!error!!! method %s not found' % method
        return result

    result = []
    if not multiple_input:
        if data != '':
            if params is not None:
                r = func(data, *params)
            else:
                r = func(data)

            result.append(smart_text(r))

        result = ''.join(result)
    else:
        data_list = data.splitlines()
        data_list = [t for t in data_list if t != '']
        for text in data_list:
            if params is not None:
                r = func(text, *params)
            else:
                r = func(text)

            result.append(smart_text(r))

        result = '\n'.join(result)

    return result


class UtilityHandler(APIHandler):
    def post(self):
        if self.request.json is None:
            return self.fail()

        method = self.request.json.get('method')
        data = self.request.json.get('data')
        params = self.request.json.get('params')
        multiple_input = self.request.json.get('multiple_input', False)
        if method is None or data is None:
            return self.fail()

        try:
            result = do_utility_handle(method, data, params, multiple_input)
        except Exception as e:
            logger.exception(e)
            result = '!!!error!!! %s' % e

        if result is None:
            result = '!!!error!!!'
        return self.success(result)
