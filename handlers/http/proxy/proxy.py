# -*- coding: utf-8 -*-
# Created by restran on 2018/5/29
from __future__ import unicode_literals, absolute_import

import socket
import ssl
import sys
from datetime import datetime

import records
import tornado.curl_httpclient
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.httputil
import tornado.ioloop
import tornado.iostream
import tornado.web
from mountains import logging
from mountains.utils import ObjectDict
from tornado import gen
from tornado.gen import is_future
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError
from tornado.httputil import HTTPHeaders
from tornado.web import RequestHandler

from handlers.http.proxy.utils import wrap_socket

logger = logging.getLogger(__name__)

ASYNC_HTTP_MAX_CLIENTS = 100
ASYNC_HTTP_CONNECT_TIMEOUT = 60
ASYNC_HTTP_REQUEST_TIMEOUT = 120

try:
    # curl_httpclient is faster than simple_httpclient
    AsyncHTTPClient.configure(
        'tornado.curl_httpclient.CurlAsyncHTTPClient',
        max_clients=ASYNC_HTTP_MAX_CLIENTS)
except ImportError:
    AsyncHTTPClient.configure(
        'tornado.simple_httpclient.SimpleAsyncHTTPClient')


class ProxyHandler(RequestHandler):
    SUPPORTED_METHODS = ['GET', 'POST', 'CONNECT', 'HEAD', 'PUT', 'DELETE', 'OPTIONS', 'PATCH']

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.response_body = None
        if self.application.interceptor_cls is not None:
            self.interceptor = self.application.interceptor_cls(self)
        else:
            self.interceptor = None

        self.database = self.application.database
        self.http_history = ObjectDict()
        self.http_history.request = ObjectDict()
        self.http_history.response = ObjectDict()
        self.response = self.http_history.response

    def http_request_history(self):
        pass
        # history_uuid = text_type(uuid.uuid4()).replace('-', '')
        # sql = 'insert into http_history (uuid, url, request_header, request_body, request_date, extra_data) ' \
        #       'values (:uuid, :url, :request_header, :request_body, :request_date, :status_code, :extra_data)'
        # params = {
        #     'uuid': history_uuid,
        #     'url': self.http_history.request.url,
        #     'request_headers': headers_2_str(self.http_history.request.headers)
        # }
        # self.database.query(sql)

    def http_response_history(self):
        pass
        # sql = 'insert into http_history (url, request, response, request_date, elapsed, status_code, extra_data) ' \
        #       'values (:url, :request, :response, :request_date, :elapsed, :status_code, :extra_data)'
        # self.database.query(sql)

    def data_received(self, chunk):
        if chunk:
            if not self.response_body:
                self.response_body = chunk
            else:
                self.response_body += chunk

    @gen.coroutine
    def get(self):
        yield self._do_fetch('GET')

    @gen.coroutine
    def post(self):
        yield self._do_fetch('POST')

    @gen.coroutine
    def head(self):
        yield self._do_fetch('HEAD')

    @gen.coroutine
    def options(self):
        yield self._do_fetch('OPTIONS')

    @gen.coroutine
    def put(self):
        yield self._do_fetch('PUT')

    @gen.coroutine
    def delete(self):
        yield self._do_fetch('DELETE')

    def _clean_headers(self):
        """
        清理headers中不需要的部分
        :return:
        """
        headers = self.request.headers
        new_headers = HTTPHeaders()
        # 如果 header 有的是 str，有的是 unicode
        # 会出现 422 错误
        for name, value in headers.get_all():
            if name == ('Content-Length', 'Connection', 'Pragma', 'Cache-Control'):
                pass
            else:
                new_headers.add(name, value)

        return new_headers

    @gen.coroutine
    def _do_fetch(self, method):
        # 清理和处理一下 header
        headers = self._clean_headers()
        try:
            if method in ('POST', 'PUT'):
                body = self.request.body
            else:
                # method in ['GET', 'HEAD', 'OPTIONS', 'DELETE']
                # GET 方法 Body 必须为 None，否则会出现异常
                body = None

            # 设置超时时间
            async_http_connect_timeout = ASYNC_HTTP_CONNECT_TIMEOUT
            async_http_request_timeout = ASYNC_HTTP_REQUEST_TIMEOUT

            # Hook request
            yield self.process_hook('on_request')

            if self.request.host in self.request.uri.split('/'):  # Normal Proxy Request
                url = self.request.uri
            else:  # Transparent Proxy Request
                # 当使用 https 的 intercept_https 时，会走这里
                url = self.request.protocol + "://" + self.request.host + self.request.uri

            # 插入访问日志
            self.http_history.request.url = url
            self.http_history.request.method = method
            self.http_history.request.date = datetime.now()
            self.http_history.request.headers = self.request.headers
            self.http_history.request.body = body if body is not None else ''
            self.http_request_history()

            response = yield AsyncHTTPClient().fetch(
                HTTPRequest(url=url,
                            method=method,
                            body=body,
                            headers=headers,
                            decompress_response=True,
                            proxy_host=self.application.proxy_ip,
                            proxy_port=self.application.proxy_port,
                            allow_nonstandard_methods=True,
                            connect_timeout=async_http_connect_timeout,
                            request_timeout=async_http_request_timeout,
                            validate_cert=False,
                            follow_redirects=False))
            yield self._on_proxy(response)
        except HTTPError as x:
            if hasattr(x, 'response') and x.response:
                yield self._on_proxy(x.response)
            else:
                self.set_status(502)
                self.write('502 Bad Gateway')
        except Exception as e:
            logger.exception(e)
            self.set_status(502)
            self.write('502 Bad Gateway')

    @gen.coroutine
    def _on_proxy(self, response):
        self.response_body = response.body if response.body else self.response_body
        self.response.code = response.code
        self.response.reason = response.reason
        self.response.body = self.response_body
        self.response.headers = response.headers
        # # Hook response
        yield self.process_hook('on_response')

        try:
            # 如果response.code是非w3c标准的，而是使用了自定义，就必须设置reason，
            # 否则会出现unknown status code的异常
            self.set_status(self.response.code, self.response.reason)
        except ValueError:
            self.set_status(self.response.code, 'Unknown Status Code')

        # 这里要用 get_all 因为要按顺序
        for (k, v) in self.response.headers.get_all():
            if k in ('Transfer-Encoding', 'Content-Length', 'Content-Encoding'):
                pass
            elif k == 'Set-Cookie':
                self.add_header(k, v)
            else:
                self.set_header(k, v)

        if self.response.code != 304 and self.response.body is not None:
            self.write(self.response.body)

        self.finish()
        # Hook finished
        yield self.process_hook('on_finished')

    @gen.coroutine
    def process_hook(self, method):
        # Hook
        m = getattr(self.interceptor, method, None)
        if m and callable(m):
            try:
                result = m()
                if is_future(result):
                    yield result
            except Exception as e:
                logger.exception(e)

    @gen.coroutine
    def connect(self):
        if self.application.intercept_https:
            self.connect_intercept()
        else:
            self.connect_relay()

    def connect_intercept(self):
        """
        This function gets called when a connect request is received.
        * The host and port are obtained from the request uri
        * A socket is created, wrapped in ssl and then added to SSLIOStream
        * This stream is used to connect to speak to the remote host on given port
        * If the server speaks ssl on that port, callback start_tunnel is called
        * An OK response is written back to client
        * The client side socket is wrapped in ssl
        * If the wrapping is successful, a new SSLIOStream is made using that socket
        * The stream is added back to the server for monitoring
        """
        host, port = self.request.uri.split(':')

        def start_tunnel():
            try:
                self.request.connection.stream.write(b"HTTP/1.1 200 OK CONNECTION ESTABLISHED\r\n\r\n")
                wrap_socket(self.request.connection.stream.socket, host, success=ssl_success)
            except tornado.iostream.StreamClosedError:
                pass
            except Exception as ex:
                logger.exception(ex)

        def ssl_success(client_socket):
            client = tornado.iostream.SSLIOStream(client_socket)
            server.handle_stream(client, self.application.listen_ip)  # lint:ok

        try:
            s = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0))
            upstream = tornado.iostream.SSLIOStream(s)
            upstream.connect((host, int(port)), start_tunnel, host)
        except Exception as e:
            logger.error(e)
            logger.error(("[!] Dropping CONNECT request to " + self.request.uri))
            self.write(b"404 Not Found")
            self.finish()

    def connect_relay(self):
        host, port = self.request.uri.split(':')
        client = self.request.connection.stream

        def read_from_client(data):
            upstream.write(data)

        def read_from_upstream(data):
            client.write(data)

        def client_close(data=None):
            if upstream.closed():
                return
            if data:
                upstream.write(data)
            upstream.close()

        def upstream_close(data=None):
            if client.closed():
                return
            if data:
                client.write(data)
            client.close()

        def start_tunnel():
            client.read_until_close(client_close, read_from_client)
            upstream.read_until_close(upstream_close, read_from_upstream)
            client.write(b'HTTP/1.0 200 Connection established\r\n\r\n')

        def on_proxy_response(data=None):
            if data:
                first_line = data.splitlines()[0]
                http_v, status, text = first_line.split(None, 2)
                if int(status) == 200:
                    start_tunnel()
                    return

            self.set_status(500)
            self.finish()

        def start_proxy_tunnel():
            upstream.write('CONNECT %s HTTP/1.1\r\n' % self.request.uri)
            upstream.write('Host: %s\r\n' % self.request.uri)
            upstream.write('Proxy-Connection: Keep-Alive\r\n\r\n')
            upstream.read_until('\r\n\r\n', on_proxy_response)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        upstream = tornado.iostream.IOStream(s)

        if self.application.proxy_ip and self.application.proxy_port:
            upstream.connect((self.application.proxy_ip, self.application.proxy_port), start_proxy_tunnel)
        else:
            upstream.connect((host, int(port)), start_tunnel)


class ProxyServer(object):
    def __init__(self, handler,
                 interceptor_source_code,
                 listen_ip="0.0.0.0",
                 listen_port=8088,
                 proxy_ip=None, proxy_port=None):
        self.application = tornado.web.Application(
            handlers=[
                (r".*", handler)
            ], debug=False,
        )
        self.application.listen_ip = listen_ip
        self.application.listen_port = listen_port
        self.application.proxy_ip = proxy_ip
        self.application.proxy_port = proxy_port
        self.application.intercept_https = True
        self.application.interceptor_cls = self.load_interceptor(interceptor_source_code)
        from settings import DATA_BASE_PATH
        logger.info('database path %s' % DATA_BASE_PATH)
        self.application.database = records.Database('sqlite:///%s' % DATA_BASE_PATH)

        global server
        server = tornado.httpserver.HTTPServer(self.application, decompress_request=True)
        self.server = server
        self.instance = None

    def start(self):
        logger.info('proxy start')
        # 为了能在线程中启动 tornado 的 event_loop
        import asyncio
        asyncio.set_event_loop(asyncio.new_event_loop())
        try:
            self.server.listen(self.application.listen_port, self.application.listen_ip)
            self.instance = tornado.ioloop.IOLoop.instance()
            self.instance.start()
            logger.warning("Shutting down the IOLoop")
        except Exception as e:
            logger.exception(e)

    def stop(self):
        if self.instance is not None:
            self.instance.stop()
            self.server.stop()

        logger.warning("Shutting down the proxy server")

    def load_interceptor(self, source):
        if source in (None, ''):
            return None

        from mountains import text_type
        import imp
        import uuid
        try:
            mod_name = 'Interceptor_%s' % text_type(uuid.uuid4()).replace('-', '')[10:-10]
            mod = sys.modules.setdefault(mod_name, imp.new_module(mod_name))
            code = compile(source, '<string>', 'exec')
            # mod.__file__ = mod_name
            mod.__package__ = ''
            exec(code, mod.__dict__)
            return getattr(mod, 'Interceptor', None)
        except:
            return None


if __name__ == "__main__":
    interceptor_code = open('./addons/test1.py').read()
    proxy = ProxyServer(None, ProxyHandler, interceptor_code)
    try:
        proxy.start()
    except KeyboardInterrupt:
        proxy.stop()
