# -*- coding: utf-8 -*-
# Created by restran on 2017/10/13
from __future__ import unicode_literals, absolute_import

import logging

from handlers.crypto import handlers
from utils import APIHandler
from bottle import get, post, request
from future.moves.urllib.parse import urlparse, urljoin
from mountains.http import read_request_from_str, request as do_request
import requests

logger = logging.getLogger(__name__)


def http_request():
    if request.json is None:
        return APIHandler.fail()

    netloc = request.json.get('netloc', '').strip()
    request_data = request.json.get('request', '').lstrip()
    if netloc == '':
        return APIHandler.fail(msg='请求的网址不能为空')
    if netloc == '' or request_data == '':
        return APIHandler.fail(msg='请求的数据不能为空')

    try:
        url_parsed = urlparse(netloc)
        url = '%s://%s' % (url_parsed.scheme, url_parsed.netloc)
        headers, method, uri, host, body = read_request_from_str(request_data)
        url = urljoin(url, uri)
        r = do_request(method, url, headers, body)
        response_data = []
        for k, v in r.headers.items():
            response_data.append('%s: %s' % (k, v))

        response_data.append('')
        response_data.append(r.text)
        result = '\n'.join(response_data)
    except Exception as e:
        logger.exception(e)
        result = '!!!error!!! %s' % e

    if result is None:
        result = '!!!error!!!'

    return APIHandler.success(result)