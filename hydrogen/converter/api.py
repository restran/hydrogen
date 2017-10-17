# -*- coding: utf-8 -*-
# Created by restran on 2017/10/13
from __future__ import unicode_literals, absolute_import
from converter.handlers import converter
from mountains import force_text, force_bytes, text_type
from base64 import b64encode
from flask import request
from utils import APIHandler
import logging

logger = logging.getLogger(__name__)


def do_convert(method, data, params):
    # data = force_text(converter.from_base64(data))
    split_list = [t for t in data.split(' ') if t != '']
    if method == 'all_digit_convert':
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
        if params is not None:

            result = [text_type(func(t, *params)) for t in split_list]
        else:
            result = [text_type(func(t)) for t in split_list]

        result = '   '.join(result)
    else:
        result = '!!!error!!! method %s not found' % method

    return result


def convert_data():
    if request.json is None:
        return APIHandler.fail()

    method = request.json.get('method')
    data = request.json.get('data')
    params = request.json.get('params')
    if method is None or data is None:
        return APIHandler.fail()

    try:
        result = do_convert(method, data, params)
    except Exception as e:
        logger.exception(e)
        result = '!!!error!!! %s' % e

    if result is None:
        result = '!!!error!!!'
    return APIHandler.success(result)
