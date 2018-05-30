# -*- coding: utf-8 -*-
# Created by restran on 2017/10/13
from __future__ import unicode_literals, absolute_import

import logging
import time
from threading import Thread

import requests
from bottle import request
from future.moves.urllib.parse import urlparse, urljoin
from mountains.http import read_request_from_str, random_agent

from utils import APIHandler
from .proxy.proxy import ProxyServer, ProxyHandler

logger = logging.getLogger(__name__)


def do_request(method, url, headers=None, data=None, session=None,
               verify=False, allow_redirects=False):
    """
    :param allow_redirects:
    :param verify:
    :type session requests.session
    :param method:
    :param url:
    :param headers:
    :param data:
    :param session:
    :return:
    """
    base_headers = {}

    if headers is None or not isinstance(headers, dict):
        headers = {}
    elif 'User-Agent' not in headers:
        headers['User-Agent'] = random_agent()

    base_headers.update(headers)

    if 'Content-Length' in base_headers:
        del base_headers['Content-Length']

    headers = base_headers
    if session is not None:
        req = session.request
    else:
        req = requests.request

    r = req(method, url, headers=headers, data=data,
            verify=verify, allow_redirects=allow_redirects)
    return r


proxy_server = None


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


def http_proxy():
    if request.json is None:
        return APIHandler.fail()

    listen_ip = request.json.get('listen_ip', '').strip()
    listen_port = request.json.get('listen_port', '').strip()
    upstream_ip = request.json.get('upstream_ip', '').strip()
    upstream_port = request.json.get('upstream_port', '').strip()
    action = request.json.get('action', '').strip()

    if listen_ip == '' or listen_port == '':
        return APIHandler.fail(msg='监听地址不能为空')

    if upstream_ip == '':
        upstream_ip = None

    if upstream_port == '':
        upstream_port = None

    global proxy_server
    if action == 'stop':
        if proxy_server is not None:
            proxy_server.stop()
            time.sleep(3)
            proxy_server = None
    else:
        if proxy_server is None:
            proxy_server = ProxyServer(ProxyHandler, listen_ip, listen_port, upstream_ip, upstream_port)
            try:
                Thread(target=proxy_server.start).start()
            except Exception as e:
                logger.exception(e)
                result = '!!!error!!! %s' % e

    return APIHandler.success()


def http_interceptor():
    if request.json is None:
        return APIHandler.fail()

    name = request.json.get('name', '').strip()
    code = request.json.get('code', '')
    entry_id = request.json.get('id', None)

    if name == '' or code == '':
        return APIHandler.fail(msg='名称或代码不能为空')

    return APIHandler.success()
