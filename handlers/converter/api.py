# -*- coding: utf-8 -*-
# Created by restran on 2017/10/13
from __future__ import unicode_literals, absolute_import

import logging
from base64 import b64encode

from mountains import text_type, force_bytes, force_text

from handlers.converter.handlers import converter, what_encode as what_encode_handler
from handlers.converter.handlers.what_code_scheme import detect_code_scheme
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
    return s


def do_convert(method, data, params, multiple_input):
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
        multiple_input = self.request.json.get('multiple_input', False)
        if method is None or data is None:
            return self.fail()

        try:
            result = do_convert(method, data, params, multiple_input)
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


class FileConverter(APIHandler):
    def post(self):
        file_content = self.request.files.get('file')[0].body
        encoding = text_type(self.get_body_argument('encoding', 'Hex'))

        if encoding == 'Hex':
            content = force_bytes(file_content).hex()
        elif encoding == 'Base64':
            content = b64encode(force_bytes(file_content))
        elif encoding == 'Decimal':
            content = force_bytes(file_content).hex()
            content = text_type(int(content, 16))
        else:
            content = file_content

        data = {
            'content': content
        }
        return self.success(data)
