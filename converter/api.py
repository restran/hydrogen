# -*- coding: utf-8 -*-
# Created by restran on 2017/10/13
from __future__ import unicode_literals, absolute_import
from magnetos.util import converter
from flask import request
from utils import APIHandler
import logging

logger = logging.getLogger(__name__)


def do_convert(method, data):
    if hasattr(converter, method):
        data = converter.from_base64(data)
        result = getattr(converter, method)(data)
    else:
        result = '!!!error!!!'

    return result


def convert_data():
    if request.json is None:
        return APIHandler.fail()

    method = request.json.get('method')
    data = request.json.get('data')
    if method is None or data is None:
        return APIHandler.fail()

    try:
        result = do_convert(method, data)
    except Exception as e:
        logger.error(e)
        result = '!!!error!!! %s' % e

    return APIHandler.success(result)
