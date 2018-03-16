# -*- coding: utf-8 -*-
# Created by restran on 2017/10/12
from __future__ import unicode_literals, absolute_import

import logging
import socket
import string
from mountains import json
from bottle import response
from importlib import import_module

logger = logging.getLogger(__name__)


def jsonify(code, data, msg):
    data = {
        'data': data,
        'code': code,
        'msg': msg
    }
    data = json.dumps(data)

    response.content_type = 'application/json; charset=utf-8'
    return data


class APIStatusCode(object):
    SUCCESS = 200  # 成功
    FAIL = 400  # 客户端的错误, 例如请求信息不正确
    ERROR = 500  # 服务端的错误, 例如出现异常
    LOGIN_REQUIRED = 401  # 需要登录才能访问


class APIHandler(object):
    @classmethod
    def return_json(cls, code, data, msg):
        try:
            return jsonify(code=code, data=data, msg=msg)
        except Exception as e:
            logger.error(e)
            return jsonify(code=APIStatusCode.ERROR, data=data, msg=msg)

    @classmethod
    def success(cls, data=None, msg='', code=APIStatusCode.SUCCESS):
        return cls.return_json(code, data, msg)

    @classmethod
    def fail(cls, data=None, msg='', code=APIStatusCode.FAIL):
        return cls.return_json(code, data, msg)

    @classmethod
    def login_required(cls, data=None, msg='', code=APIStatusCode.LOGIN_REQUIRED):
        return cls.return_json(code, data, msg)

    @classmethod
    def error(cls, data=None, msg='', code=APIStatusCode.ERROR):
        return cls.return_json(code, data, msg)


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
