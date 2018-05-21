# -*- coding: utf-8 -*-
# Created by restran on 2017/10/13
from __future__ import unicode_literals, absolute_import

import logging

from handlers.crypto import handlers
from utils import APIHandler
from bottle import get, post, request
from .utils import make_private_key_pem, make_public_key_pem, \
    read_rsa_pem_key, rsa_decrypt, rsa_encrypt

logger = logging.getLogger(__name__)


def do_decode(method, data, params):
    # 不能用 import string 的方式，否则打包成 exe 后会无法 import
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

        def _do_decode(d):
            if params is not None:
                _result = decode_func(d, *params, verbose=True)
            else:
                _result = decode_func(d, verbose=True)

            return _result

        if method in ('manchester',):
            index = 0
            last_index = 0
            data += ' '
            length = len(data)
            result = []
            # 输入的时候是以什么字符分隔，输出的时候保持一致
            while index < length:
                t = data[index]
                if t in (' ', '\n'):
                    text = data[last_index:index]
                    last_index = index + 1
                    if text != '':
                        r = _do_decode(text)
                        result.append(r)

                    result.append(t)
                index += 1

            result = ''.join(result)
            result = result.rstrip(' ')
        else:
            result = _do_decode(data)

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


def rsa_from_pem_key():
    """
    读取 PEM 格式的 rsa 密钥
    openssl中RSA私钥文件生成命令为：
    openssl genrsa -out private_rsa.pem 1024
    已知私钥，生成RSA公钥命令为：
    openssl rsa -in private_rsa.pem -pubout -out public_rsa.pem
    :return:
    """
    if request.json is None:
        return APIHandler.fail()

    key_content = request.json.get('key_content', '')
    if key_content == '':
        return APIHandler.fail(msg='RSA密钥不能为空')

    try:
        data = read_rsa_pem_key(key_content)
    except Exception as e:
        msg = '%s, %s' % ('识别失败', e)
        return APIHandler.fail(msg=msg)

    return APIHandler.success(data)


def rsa_to_pem_key():
    """
    转成 PEM 格式的 rsa 密钥
    :return:
    """

    if request.json is None:
        return APIHandler.fail()

    n = request.json.get('n', '')
    e = request.json.get('e', '')
    p = request.json.get('p', '')
    q = request.json.get('q', '')

    if n == '':
        return APIHandler.fail(msg='n不能为空')
    if e == '':
        return APIHandler.fail(msg='e不能为空')

    if (p == '' and q != '') or (p != '' and q == ''):
        return APIHandler.fail(msg='p和q不能为空')

    try:
        if p != '' and q != '':
            key_content = make_private_key_pem(n, e, p, q)
            is_private = True
        else:
            key_content = make_public_key_pem(n, e)
            is_private = False
    except Exception as e:
        msg = '%s, %s' % ('转成PEM格式密钥失败', e)

        return APIHandler.fail(msg=msg)
    data = {
        'key_content': key_content,
        'n': n,
        'e': e,
        'p': p,
        'q': q,
        'is_private': is_private
    }

    return APIHandler.success(data)


def rsa_encrypt_decrypt():
    """
    rsa 加解密
    :return:
    """

    if request.json is None:
        return APIHandler.fail()

    n = request.json.get('n', '')
    e = request.json.get('e', '')
    p = request.json.get('p', '')
    q = request.json.get('q', '')
    plain = request.json.get('plain', '')
    cipher = request.json.get('cipher', '')
    action = request.json.get('action', '')

    if n == '':
        return APIHandler.fail(msg='n不能为空')
    if e == '':
        return APIHandler.fail(msg='e不能为空')

    if (p == '' and q != '') or (p != '' and q == ''):
        return APIHandler.fail(msg='p和q不能为空')

    try:
        if action == 'decrypt':
            if p != '' and q != '':
                plain = rsa_decrypt(cipher, e, p, q)
            else:
                return APIHandler.fail(msg='p和q不能为空')
        else:
            if n != '' and e != '':
                cipher = rsa_encrypt(plain, n, e)
            else:
                return APIHandler.fail(msg='n和e不能为空')

    except Exception as e:
        msg = '%s, %s' % ('RSA加解密失败', e)

        return APIHandler.fail(msg=msg)
    data = {
        'plain': str(plain),
        'cipher': str(cipher),
    }

    return APIHandler.success(data)
