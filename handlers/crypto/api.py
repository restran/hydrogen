# -*- coding: utf-8 -*-
# Created by restran on 2017/10/13
from __future__ import unicode_literals, absolute_import

import logging

from mountains import text_type

from handlers.crypto import handlers
from utils import APIHandler
from .utils import RSAHelper, AESHelper

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


class DecodeData(APIHandler):
    def post(self):
        if self.request.json is None:
            return self.fail()
        method = self.request.json.get('method')
        data = self.request.json.get('data')
        params = self.request.json.get('params')
        if method is None or data is None:
            return self.fail()

        try:
            result = do_decode(method, data, params)
        except Exception as e:
            logger.exception(e)
            result = '!!!error!!! %s' % e

        if result is None:
            result = '!!!error!!!'

        return self.success(result)


class RSAFromPEMKey(APIHandler):
    """
    读取 PEM 格式的 rsa 密钥
    openssl中RSA私钥文件生成命令为：
    openssl genrsa -out private_rsa.pem 1024
    已知私钥，生成RSA公钥命令为：
    openssl rsa -in private_rsa.pem -pubout -out public_rsa.pem
    :return:
    """

    def post(self):
        if self.request.json is None:
            return self.fail()

        if self.request.json is None:
            return self.fail()

        key_content = self.request.json.get('key_content', '')
        passphrase = self.request.json.get('passphrase', None)
        if key_content == '':
            return self.fail(msg='RSA密钥不能为空')

        try:
            data = RSAHelper(passphrase=passphrase).read_rsa_pem_key(key_content)
        except Exception as e:
            logger.exception(e)
            msg = '%s, %s' % ('识别失败', e)
            return self.fail(msg=msg)

        return self.success(data)


class RSAToPEMKey(APIHandler):
    """
    转成 PEM 格式的 rsa 密钥
    :return:
    """

    def post(self):
        if self.request.json is None:
            return self.fail()

        n = self.request.json.get('n', '')
        e = self.request.json.get('e', '')
        p = self.request.json.get('p', '')
        q = self.request.json.get('q', '')

        if n == '':
            return self.fail(msg='n不能为空')
        if e == '':
            return self.fail(msg='e不能为空')

        if (p == '' and q != '') or (p != '' and q == ''):
            return self.fail(msg='p和q不能为空')

        try:
            rsa = RSAHelper(n, e, p, q)
            if p != '' and q != '':
                key_content = rsa.make_private_key_pem()
                is_private = True
            else:
                key_content = rsa.make_public_key_pem()
                is_private = False
        except Exception as e:
            logger.exception(e)
            msg = '%s, %s' % ('转成PEM格式密钥失败', e)
            return self.fail(msg=msg)

        data = {
            'key_content': key_content,
            'n': n,
            'e': e,
            'p': p,
            'q': q,
            'is_private': is_private
        }

        return self.success(data)


class RSAEncryptDecrypt(APIHandler):
    """
    rsa 加解密
    :return:
    """

    def post(self):
        if self.request.json is None:
            return self.fail()

        n = self.request.json.get('n', '')
        e = self.request.json.get('e', '')
        p = self.request.json.get('p', '')
        q = self.request.json.get('q', '')
        plain = self.request.json.get('plain', '')
        cipher = self.request.json.get('cipher', '')
        action = self.request.json.get('action', '')
        padding = self.request.json.get('padding', 'NoPadding')
        plain_encoding = self.request.json.get('plain_encoding', 'Decimal')
        cipher_encoding = self.request.json.get('cipher_encoding', 'Decimal')

        if n == '':
            return self.fail(msg='n不能为空')
        if e == '':
            return self.fail(msg='e不能为空')

        if (p == '' and q != '') or (p != '' and q == ''):
            return self.fail(msg='p和q不能为空')

        try:
            rsa = RSAHelper(n, e, p, q, padding=padding,
                            plain_encoding=plain_encoding,
                            cipher_encoding=cipher_encoding)
            if action == 'decrypt':
                if p != '' and q != '':
                    plain = rsa.decrypt(cipher)
                else:
                    return self.fail(msg='p和q不能为空')
            else:
                if n != '' and e != '':
                    cipher = rsa.encrypt(plain)
                else:
                    return self.fail(msg='n和e不能为空')

        except Exception as e:
            logger.exception(e)
            msg = '%s, %s' % ('RSA加解密失败', e)

            return self.fail(msg=msg)
        data = {
            'plain': str(plain),
            'cipher': str(cipher),
        }

        return self.success(data)


class AESEncryptDecrypt(APIHandler):
    """
    aes 加解密
    :return:
    """

    def post(self):
        if self.request.json is None:
            return self.fail()

        action = self.request.json.get('action', '')
        key = self.request.json.get('key', '')
        key_encoding = self.request.json.get('key_encoding', '')
        mode = self.request.json.get('mode', '')
        iv = self.request.json.get('iv', '')
        iv_encoding = self.request.json.get('iv_encoding', '')
        padding = self.request.json.get('padding', '')
        plain_encoding = self.request.json.get('plain_encoding', '')
        cipher_encoding = self.request.json.get('cipher_encoding', '')
        plain = self.request.json.get('plain', '')
        cipher = self.request.json.get('cipher', '')

        try:
            aes = AESHelper(key, iv, key_encoding, iv_encoding, mode,
                            padding, plain_encoding, cipher_encoding)
            if action == 'decrypt':
                plain = aes.decrypt(cipher)
            else:
                cipher = aes.encrypt(plain)
        except Exception as e:
            logger.exception(e)
            msg = '%s, %s' % ('AES加解密失败', e)

            return self.fail(msg=msg)

        data = {
            'plain': text_type(plain),
            'cipher': text_type(cipher),
        }

        return self.success(data)
