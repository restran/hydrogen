# -*- coding: utf-8 -*-
# Created by restran on 2017/10/12
from __future__ import unicode_literals, absolute_import

import logging
import socket
import string
from importlib import import_module

from mountains import json
from tornado.web import RequestHandler

logger = logging.getLogger(__name__)


class APIStatusCode(object):
    SUCCESS = 200  # 成功
    FAIL = 400  # 客户端的错误, 例如请求信息不正确
    ERROR = 500  # 服务端的错误, 例如出现异常
    LOGIN_REQUIRED = 401  # 需要登录才能访问


class APIHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    def __init__(self, app, request, **kwargs):
        super(APIHandler, self).__init__(app, request, **kwargs)
        self.database = app.database

    def return_json(self, code, data, msg):
        try:
            result = json.dumps({
                'data': data,
                'code': code,
                'msg': msg
            })
        except Exception as e:
            logger.error(e)
            result = json.dumps({
                'data': data,
                'code': APIStatusCode.ERROR,
                'msg': msg
            })

        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.write(result)
        self.finish()

    def initialize(self, *args, **kwargs):
        pass

    def prepare(self):
        self.request.json = {}
        if self.request.method == 'POST':
            content_type = self.request.headers.get('Content-Type', '').split(';')[0]
            if content_type == 'application/json':
                try:
                    self.request.json = json.loads(self.request.body)
                except Exception as e:
                    logger.error(e)

    def success(self, data=None, msg='', code=APIStatusCode.SUCCESS):
        return self.return_json(code, data, msg)

    def fail(self, data=None, msg='', code=APIStatusCode.FAIL):
        return self.return_json(code, data, msg)

    def login_required(self, data=None, msg='', code=APIStatusCode.LOGIN_REQUIRED):
        return self.return_json(code, data, msg)

    def error(self, data=None, msg='', code=APIStatusCode.ERROR):
        return self.return_json(code, data, msg)

    def write_error(self, status_code, **kwargs):
        self.clear()
        self.set_status(status_code)
        # 因为执行了 clear，所以把 header 也清理掉了
        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.error(
            msg='Internal Server Error' if status_code == 200 else self._reason,
            code=APIStatusCode.ERROR
        )


def is_port_open(ip, port):
    """
    检测端口是否被占用
    :param ip:
    :param port:
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except:
        return False


def import_string(module_path):
    try:
        return import_module(module_path)
    except AttributeError:
        return None


def get_raw_plain_text(raw_data, decoded_data):
    """
    因为密文中可能包含数字，符合等各种非字母的字符，一些解密的算法是不考虑这些
    在输出明文的时候，要跟这些符合，按要原来的顺序还原回来
    :param raw_data:
    :param decoded_data:
    :return:
    """
    index = 0
    plain = []
    for i, c in enumerate(raw_data):
        if c in string.ascii_lowercase:
            new_c = decoded_data[index].lower()
            index += 1
        elif c in string.ascii_uppercase:
            new_c = decoded_data[index].upper()
            index += 1
        else:
            new_c = c

        plain.append(new_c)

    return ''.join(plain)
