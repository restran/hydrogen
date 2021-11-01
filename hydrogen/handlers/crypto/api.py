# -*- coding: utf-8 -*-
# Created by restran on 2017/10/13
from __future__ import unicode_literals, absolute_import

import logging

from mountains import text_type

from handlers.crypto import handlers
from utils import APIHandler
from utils.find_ctf_flag import find_flag, get_flag_from_string, clean_find_ctf_flag_result
from .utils import RSAHelper, AESHelper, DESHelper

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

        if isinstance(result, list):
            result = '\n'.join(result)

        return self.success(result)


class FuzzingDecodeData(APIHandler):
    def post(self):
        if self.request.json is None:
            return self.fail()

        data = self.request.json.get('data')
        params = self.request.json.get('params')
        if data is None:
            return self.fail()

        method_list = [
            'atbash_cipher', 'bacon_case_cipher', 'bacon_cipher', 'caesar', 'caesar_inc_dec',
            'caesar_inc_dec_printable', 'caesar_odd_even', 'caesar_printable', 'caesar_rail_fence',
            'manchester', 'mobile_keyboard', 'modified_base64', 'pigpen_cipher',
            'polybius_square', 'quoted_printable', 'qwerty_cipher', 'rail_fence',
            'rot13', 'shadow_code', 'vigenere', 'xxencode', 'xor_crack'
        ]

        flag_result_dict = {}
        for method in method_list:
            try:
                result = do_decode(method, data, params)
                if not isinstance(result, list):
                    result = result.splitlines()

                # 因为输出结果是一行一行的，每行去识别flag更精确，而不是全部当成一行字符串
                for line in result:
                    get_flag_from_string(line, result_dict=flag_result_dict)
            except:
                pass

        result = '\n'.join(flag_result_dict.keys())
        if result == '':
            result = '!!!nothing found!!!'
        else:
            result_list = clean_find_ctf_flag_result(result)
            result = '\n'.join(result_list)
        return self.success(result)


class FindFlagFromString(APIHandler):
    def post(self):
        if self.request.json is None:
            return self.fail()

        data = self.request.json.get('data')
        if data is None:
            return self.fail()

        if not isinstance(data, list):
            data = [data]

        result_dict = {}
        for content in data:
            if content == '':
                continue

            find_flag(content, result_dict=result_dict)

        result = '\n'.join(result_dict.keys())
        if result == '':
            result = '!!!nothing found!!!'
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

        n = self.request.json.get('n', '').strip()
        e = self.request.json.get('e', '').strip()
        p = self.request.json.get('p', '').strip()
        q = self.request.json.get('q', '').strip()

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
    私钥加密公钥可以解密
    公钥加密私钥可以解密
    (N,e)是公钥，(N,d)是私钥
    :return:
    """

    def post(self):
        if self.request.json is None:
            return self.fail()

        n = self.request.json.get('n', '')
        e = self.request.json.get('e', '')
        p = self.request.json.get('p', '')
        q = self.request.json.get('q', '')
        d = self.request.json.get('d', '')
        plain = self.request.json.get('plain', '')
        cipher = self.request.json.get('cipher', '')
        action = self.request.json.get('action', '')
        padding = self.request.json.get('padding', 'NoPadding')
        plain_encoding = self.request.json.get('plain_encoding', 'Decimal')
        cipher_encoding = self.request.json.get('cipher_encoding', 'Decimal')
        # 加密方式，公钥加密，私钥解密，还是私钥加密，公钥解密
        encrypt_method = self.request.json.get('encrypt_method', 'public-key-encrypt')

        if e == '':
            return self.fail(msg='e不能为空')

        if (p == '' and q != '') or (p != '' and q == ''):
            return self.fail(msg='p和q不能为空')

        if n == '' and (p == '' or q == ''):
            return self.fail(msg='n不能为空')

        try:
            rsa = RSAHelper(n, e, p, q, d, padding=padding,
                            plain_encoding=plain_encoding,
                            cipher_encoding=cipher_encoding,
                            encrypt_method=encrypt_method)

            if action == 'decrypt':
                if encrypt_method == 'public-key-encrypt':
                    if (p != '' and q != '') or d != '':
                        if cipher == '':
                            return self.fail(msg='密文不能为空')
                        plain = rsa.decrypt(cipher)
                    else:
                        return self.fail(msg='p和q或者d不能为空')
                else:
                    if n != '' and e != '':
                        if cipher == '':
                            return self.fail(msg='密文不能为空')
                        plain = rsa.decrypt(cipher)
                    else:
                        return self.fail(msg='n和e不能为空')
            else:
                if encrypt_method == 'public-key-encrypt':
                    if (n != '' or (p != '' and q != '')) and e != '':
                        if plain == '':
                            return self.fail(msg='明文不能为空')

                        cipher = rsa.encrypt(plain)
                    else:
                        return self.fail(msg='n和e不能为空')
                else:
                    if ((p != '' and q != '') or d != '') and e != '':
                        if plain == '':
                            return self.fail(msg='明文不能为空')

                        cipher = rsa.encrypt(plain)
                    else:
                        return self.fail(msg='p、q或者d和e不能为空')

        except Exception as e:
            logger.exception(e)
            msg = '%s, %s' % ('RSA加解密失败', e)

            return self.fail(msg=msg)

        data = {
            'plain': str(plain),
            'cipher': str(cipher),
        }

        return self.success(data)


class RSACalcD(APIHandler):
    """
    根据 p、q、e 计算 d
    :return:
    """

    def post(self):
        if self.request.json is None:
            return self.fail()

        e = self.request.json.get('e', '').strip()
        p = self.request.json.get('p', '').strip()
        q = self.request.json.get('q', '').strip()

        if e == '':
            return self.fail(msg='e不能为空')

        if p == '' or q == '':
            return self.fail(msg='p和q不能为空')

        try:
            rsa = RSAHelper(n=None, e=e, p=p, q=q)
            d = rsa.calc_d()
            # 如果不转成字符串，会表示成科学计数法
            return self.success(str(d))
        except Exception as e:
            return self.error(msg=str(e))


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


class DESEncryptDecrypt(APIHandler):
    """
    des 加解密
    :return:
    """

    def post(self):
        if self.request.json is None:
            return self.fail()

        action = self.request.json.get('action', '')
        is_triple_des = self.request.json.get('is_triple_des', False)
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
            des = DESHelper(key, iv, key_encoding, iv_encoding, mode,
                            padding, plain_encoding, cipher_encoding, is_triple_des)
            if action == 'decrypt':
                plain = des.decrypt(cipher)
            else:
                cipher = des.encrypt(plain)
        except Exception as e:
            logger.exception(e)
            msg = '%s, %s' % ('DES加解密失败', e)

            return self.fail(msg=msg)

        data = {
            'plain': text_type(plain),
            'cipher': text_type(cipher),
        }

        return self.success(data)
