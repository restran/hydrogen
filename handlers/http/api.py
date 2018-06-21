# -*- coding: utf-8 -*-
# Created by restran on 2017/10/13
from __future__ import unicode_literals, absolute_import

import logging
import time
import uuid
from datetime import datetime
from threading import Thread

import requests
from future.moves.urllib.parse import urlparse, urljoin
from mountains import text_type
from mountains.datetime.converter import datetime2str
from mountains.http import read_request_from_str, DEFAULT_USER_AGENT

from handlers.http.proxy.proxy import ProxyServer, ProxyHandler
from utils import APIHandler

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
        headers['User-Agent'] = DEFAULT_USER_AGENT

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


class HTTPRequest(APIHandler):
    def post(self):
        if self.request.json is None:
            return self.fail()

        netloc = self.request.json.get('netloc', '').strip()
        request_data = self.request.json.get('request', '').lstrip()
        if netloc == '':
            return self.fail(msg='请求的网址不能为空')
        if netloc == '' or request_data == '':
            return self.fail(msg='请求的数据不能为空')

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

        return self.success(result)


class HTTPProxy(APIHandler):
    def post(self):
        if self.request.json is None:
            return self.fail()

        listen = self.request.json.get('listen', '').strip()
        upstream = self.request.json.get('upstream', '').strip()

        action = self.request.json.get('action', '').strip()
        interceptor = self.request.json.get('interceptor', '')

        try:
            listen_ip, listen_port = listen.split(':')
            if upstream != '':
                upstream_ip, upstream_port = upstream.split(':')
                upstream_port = int(upstream_port)
            else:
                upstream_ip, upstream_port = None, None
        except Exception as e:
            return self.fail(msg='%s' % e)

        if listen_ip == '' or listen_port == '':
            return self.fail(msg='监听地址不能为空')

        if interceptor not in (None, ''):
            sql = 'select * from interceptor where uuid=:uuid limit 1'
            params = {
                'uuid': interceptor
            }
            rows = self.database.query(sql, **params).as_dict()
            if len(rows) <= 0:
                return self.fail(msg='查找不到该 Interceptor')
            interceptor_code = rows[0]['code']
        else:
            interceptor_code = ''

        global proxy_server
        if action == 'stop':
            if proxy_server is not None:
                proxy_server.stop()
                time.sleep(3)
                proxy_server = None
        else:
            if proxy_server is None:
                proxy_server = ProxyServer(ProxyHandler, interceptor_code,
                                           listen_ip, listen_port, upstream_ip, upstream_port)
                try:
                    Thread(target=proxy_server.start).start()
                except Exception as e:
                    logger.exception(e)
                    result = '!!!error!!! %s' % e
                    return self.fail(msg=result)

        return self.success()


class HTTPInterceptor(APIHandler):
    def post(self):
        if self.request.json is None:
            return self.fail()

        name = self.request.json.get('name', '').strip()
        code = self.request.json.get('code', '')
        entry_uuid = self.request.json.get('uuid', None)
        action = self.request.json.get('action', '')

        if action == 'insert-update':
            if name == '' or code == '':
                return self.fail(msg='名称或代码不能为空')

            try:
                if entry_uuid is not None:
                    sql = 'update interceptor set name = :name, code = :code where uuid = :uuid'
                else:
                    entry_uuid = text_type(uuid.uuid4()).replace('-', '')
                    sql = 'insert into interceptor (name, code, uuid, create_date) ' \
                          'values (:name, :code, :uuid, :create_date)'
                params = {
                    'uuid': entry_uuid,
                    'name': name,
                    'code': code,
                    'create_date': datetime2str(datetime.now())
                }
                self.database.query(sql, **params)
                return self.success(params)
            except Exception as e:
                return self.fail(msg='%s' % e)
        elif action == 'delete':
            if entry_uuid in ('', None):
                return self.fail(msg='uuid不能为空')

            try:
                sql = 'delete from interceptor where uuid = :uuid'
                params = {
                    'uuid': entry_uuid,
                }
                self.database.query(sql, **params)
                return self.success(params)
            except Exception as e:
                return self.fail(msg='%s' % e)
        elif action == 'get-all':
            sql = 'select * from interceptor order by create_date'
            data = self.database.query(sql).as_dict()
            return self.success(data)
        else:
            return self.success()
