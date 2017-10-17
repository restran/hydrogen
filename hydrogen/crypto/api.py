# -*- coding: utf-8 -*-
# Created by restran on 2017/10/13
from __future__ import unicode_literals, absolute_import
from crypto import handlers
from converter.handlers import converter
from mountains.encoding import force_text, force_bytes
from mountains.util import any_none
from base64 import b64encode
from flask import request
from utils import APIHandler
import logging

logger = logging.getLogger(__name__)


def do_decode(method, data, params):
    h = getattr(handlers, method, None)
    if h is not None:
        # data = force_text(converter.from_base64(data))

        decode = getattr(h, 'decode', None)
        decode_all = getattr(h, 'decode_all', None)
        if decode_all is not None:
            decode_func = decode_all
        elif decode is not None:
            decode_func = decode
        else:
            return '!!!error!!! no available decode for method %s' % method

        if params is not None:
            result = decode_func(data, *params, verbose=True)
        else:
            result = decode_func(data, verbose=True)

    else:
        result = '!!!error!!! method %s not found' % method

    return result


def decode_data():
    if request.json is None:
        return APIHandler.fail()

    method = request.json.get('method')
    data = request.json.get('data')
    params = request.json.get('params')
    if method is None or data is None:
        return APIHandler.fail()

    try:
        result = do_decode(method, data, params)
    except Exception as e:
        logger.exception(e)
        result = '!!!error!!! %s' % e

    if result is None:
        result = '!!!error!!!'

    return APIHandler.success(result)
