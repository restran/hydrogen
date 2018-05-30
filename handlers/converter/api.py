# -*- coding: utf-8 -*-
# Created by restran on 2017/10/13
from __future__ import unicode_literals, absolute_import

import logging

from mountains import text_type

from handlers.converter.handlers import converter, what_encode as what_encode_handler
from handlers.converter.handlers.what_code_scheme import detect_code_scheme
from utils import APIHandler

logger = logging.getLogger(__name__)


def do_convert(method, data, params):
    # data = force_text(converter.from_base64(data))
    if method == 'all_digit_convert':
        split_list = [t for t in data.split(' ') if t != '']
        result = {}
        for t in split_list:
            r = converter.all_digit_convert(t, *params)
            for k, v in r.items():
                if k in result:
                    result[k] += '   ' + text_type(v)
                else:
                    result[k] = text_type(v)

        return result
    elif hasattr(converter, method):
        func = getattr(converter, method)
        index = 0
        last_index = 0
        data += ' '
        length = len(data)
        result = []
        # 输入的时候是以什么字符分隔，输出的时候保持一致
        while index < length:
            t = data[index]
            if t in (' ', '\n'):
                text = data[last_index:index]
                last_index = index + 1
                if text != '':
                    if params is not None:
                        r = text_type(func(text, *params))
                    else:
                        r = text_type(func(text))
                    result.append(r)

                result.append(t)
            index += 1

        result = ''.join(result)
        result = result.rstrip(' ')
    else:
        result = '!!!error!!! method %s not found' % method

    return result


class ConvertData(APIHandler):
    def post(self):
        if self.request.json is None:
            return self.fail()

        method = self.request.json.get('method')
        data = self.request.json.get('data')
        params = self.request.json.get('params')
        if method is None or data is None:
            return self.fail()

        try:
            result = do_convert(method, data, params)
        except Exception as e:
            logger.exception(e)
            result = '!!!error!!! %s' % e

        if result is None:
            result = '!!!error!!!'
        return self.success(result)


class WhatEncode(APIHandler):
    def post(self):
        if self.request.json is None:
            return self.fail()

        max_depth = self.request.json.get('max_depth')
        data = self.request.json.get('data')
        # params = request.json.get('params')
        if max_depth is None or data is None:
            return self.fail()

        result = {}
        try:
            result['scheme_list'] = detect_code_scheme(data)
        except Exception as e:
            logger.exception(e)
            result['scheme_list'] = '!!!error!!! %s' % e

        try:
            result['result'] = what_encode_handler.decode(data, max_depth)
            if result['result'] is None:
                result['result'] = '!!!error!!!'
        except Exception as e:
            logger.exception(e)
            result['result'] = '!!!error!!! %s' % e

        return self.success(result)
