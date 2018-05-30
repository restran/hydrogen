# -*- coding: utf-8 -*-
# Created by restran on 2018/5/29
from __future__ import unicode_literals, absolute_import

import asyncio
import socket
import ssl
import sys
from copy import copy

import tornado.curl_httpclient
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.httputil
import tornado.ioloop
import tornado.iostream
import tornado.web
from mountains import logging
from tornado import gen
from tornado.gen import is_future
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError
from tornado.httputil import HTTPHeaders
from tornado.web import RequestHandler
from tornado.web import asynchronous

from .utils import wrap_socket

logger = logging.getLogger(__name__)

ASYNC_HTTP_CONNECT_TIMEOUT = 60
ASYNC_HTTP_REQUEST_TIMEOUT = 120

# AsyncHTTPClient.configure('tornado.simple_httpclient.AsyncHTTPClient')

_REQUEST, _RESPONSE, _FINISHED = 0, 1, 2

# 拷贝 list
copy_list = (lambda lb: copy(lb) if lb else [])


class ProxyHandler(RequestHandler):
    SUPPORTED_METHODS = ['GET', 'POST', 'CONNECT', 'HEAD', 'PUT', 'DELETE', 'OPTIONS', 'PATCH']
    _call_mapper = {
        _REQUEST: 'on_request',
        _RESPONSE: 'on_response',
        _FINISHED: 'on_finished',
    }

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        # 拷贝一份中间件的列表
        self.middleware_list = copy_list(self.application.middleware_list)
        self.response_body = None

    def clear_nested_middleware(self, mw_class):
        """
        清除该中间件下级的所有中间件
        :param mw_class:
        :return:
        """
        # logger.debug('clear_nested_middleware')
        # logger.debug(self.middleware_list)
        for i, m in enumerate(self.middleware_list):
            if mw_class == m:
                self.middleware_list = self.middleware_list[:i]
                break

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
    def execute_next(self, request, mv_type, handler, *args, **kwargs):
        method_name = self._call_mapper.get(mv_type)
        if method_name == 'on_request':
            middleware_list = self.middleware_list
        elif method_name in ['on_response', 'on_finished']:
            # 这两个方法的处理顺序是反序
            middleware_list = self.middleware_list[-1::-1]
        else:
            return
        try:
            for mv_class in middleware_list:
                instance = mv_class(handler)
                # 如果不提供 default, 不存在时会出现异常
                m = getattr(instance, method_name, None)
                # logger.debug('%s, %s, %s' % (mv_class, m, method_name))
                if m and callable(m):
                    try:
                        result = m(*args, **kwargs)
                        if is_future(result):
                            yield result
                    except Exception as e:
                        # 在某一层的中间件出现异常,下一级的都不执行
                        self.clear_nested_middleware(mv_class)
                        # 如果在 request 阶段就出现了异常,直接进入 finish
                        if mv_type == _REQUEST and not self._finished:
                            status_code = getattr(e, 'status_code', 500)
                            logger.debug('exception write error')
                            self.write_error(status_code, exc_info=sys.exc_info())
                        # 不再往下执行
                        break
        except Exception as e:
            logger.exception(e)
            # 出现了预料之外的错误, 清理所有中间件, 结束
            self.middleware_list = []
            status_code = getattr(e, 'status_code', 500)
            self.write_error(status_code, exc_info=sys.exc_info())

    @gen.coroutine
    def _process_request(self, handler):
        logger.info('_process_request')
        yield self.execute_next(handler.request, _REQUEST, handler)

    @gen.coroutine
    def _process_response(self, handler, chunk):
        logger.info('_process_response')
        yield self.execute_next(handler.request, _RESPONSE, handler, chunk)

    @gen.coroutine
    def _process_finished(self, handler):
        logger.info('_process_finished')
        yield self.execute_next(handler.request, _FINISHED, handler)

    @gen.coroutine
    def prepare(self):
        super(ProxyHandler, self).prepare()
        logger.debug('base prepare')
        yield self._process_request(self)

    @gen.coroutine
    def finish(self, chunk=None):
        if chunk:
            self.write(chunk)
            chunk = None

        yield self._process_response(self, self._write_buffer)

        # 执行完父类的 finish 方法后, 就会开始调用 on_finish
        super(ProxyHandler, self).finish(chunk)

    def write(self, chunk):
        super(ProxyHandler, self).write(chunk)

    @gen.coroutine
    def on_finish(self):
        """
        Called after the end of a request.
        :return:
        """
        super(ProxyHandler, self).on_finish()
        yield self._process_finished(self)

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

            if self.request.host in self.request.uri.split('/'):  # Normal Proxy Request
                url = self.request.uri
            else:  # Transparent Proxy Request
                # 当使用 https 的 intercept_https 时，会走这里
                url = self.request.protocol + "://" + self.request.host + self.request.uri

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
            self._on_proxy(response)
        except HTTPError as x:
            if hasattr(x, 'response') and x.response:
                self._on_proxy(x.response)
            else:
                self.set_status(502)
                self.write('502 Bad Gateway')
        except Exception as e:
            logger.exception(e)
            self.set_status(502)
            self.write('502 Bad Gateway')

    # This function is a callback when a small chunk is received
    def _handle_data_chunk(self, data):
        if data:
            if not self.response_body:
                self.response_body = data
            else:
                self.response_body += data

    def _on_proxy(self, response):
        try:
            # 如果response.code是非w3c标准的，而是使用了自定义，就必须设置reason，
            # 否则会出现unknown status code的异常
            self.set_status(response.code, response.reason)
        except ValueError:
            self.set_status(response.code, 'Unknown Status Code')

        self.response_body = response.body if response.body else self.response_body

        # 这里要用 get_all 因为要按顺序
        for (k, v) in response.headers.get_all():
            if k in ('Transfer-Encoding', 'Content-Length', 'Content-Encoding'):
                pass
            elif k == 'Set-Cookie':
                self.add_header(k, v)
            else:
                self.set_header(k, v)

        if response.code != 304 and self.response_body is not None:
            self.write(self.response_body)

    @asynchronous
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

        global server
        server = tornado.httpserver.HTTPServer(self.application, decompress_request=True)
        self.server = server
        self.instance = None

    def start(self):
        logger.info('proxy start')
        # 为了能在线程中启动 tornado 的 event_loop
        asyncio.set_event_loop(asyncio.new_event_loop())
        try:
            self.server.listen(self.application.listen_port, self.application.listen_ip)
            self.instance = tornado.ioloop.IOLoop.instance()
            self.instance.start()
            self.server.stop()
            logger.warning("Shutting down the IOLoop")
        except Exception as e:
            logger.exception(e)

    def stop(self):
        if self.instance is not None:
            self.instance.stop()

        logger.warning("Shutting down the proxy server")


if __name__ == "__main__":
    proxy = ProxyServer(ProxyHandler)
    try:
        proxy.start()
    except KeyboardInterrupt:
        proxy.stop()
