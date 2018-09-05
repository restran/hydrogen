# -*- coding: utf-8 -*-
# created by restran on 2018/05/18
from __future__ import unicode_literals, absolute_import

import binascii
from base64 import b64decode, b64encode

from Cryptodome.Cipher import AES, PKCS1_OAEP, PKCS1_v1_5
from Cryptodome.PublicKey import RSA
from Cryptodome.Util.Padding import pad, unpad
from Cryptodome.Util.number import inverse, bytes_to_long, long_to_bytes
from mountains import force_bytes, force_text, text_type

from ..converter.handlers.converter import hex2dec
import logging

logger = logging.getLogger(__name__)


def ensure_long(c):
    if c is None:
        return c

    if not isinstance(c, int):
        if len(c) == 0:
            return None
        if c.lower().startswith('0x'):
            return int(hex2dec(c[2:]))
        else:
            return int(c)
    return c


class RSAHelper(object):
    def __init__(self, n=None, e=None, p=None, q=None, d=None, padding='NoPadding',
                 passphrase=None, plain_encoding='Decimal', cipher_encoding='Decimal'):
        self.n, self.e, self.p, self.q, self.d = ensure_long(n), ensure_long(e), \
                                                 ensure_long(p), ensure_long(q), ensure_long(d)

        if passphrase is not None and passphrase.strip() == '':
            passphrase = None

        self.passphrase = passphrase
        self.padding = padding
        self.plain_encoding = plain_encoding
        self.cipher_encoding = cipher_encoding

    def read_rsa_pem_key(self, key_content):
        n, e, p, q = '', '', '', ''

        key_content = key_content.strip()
        if self.passphrase is not None:
            rsa = RSA.importKey(key_content, self.passphrase)
        else:
            rsa = RSA.importKey(key_content)
        n = rsa.n
        e = rsa.e

        if rsa.has_private():
            p = rsa.p
            q = rsa.q
            is_private = True
        else:
            is_private = False

        data = {
            'key_content': key_content,
            'n': str(n),
            'e': str(e),
            'p': str(p),
            'q': str(q),
            'is_private': is_private
        }
        return data

    def make_private_key_pem(self):
        d = inverse(self.e, (self.p - 1) * (self.q - 1))
        rsa = RSA.construct((self.n, self.e, d))
        return rsa.exportKey()

    def make_public_key_pem(self):
        rsa = RSA.construct((self.n, self.e,))
        return rsa.publickey().exportKey()

    @classmethod
    def encoding_2_long(cls, data, encoding):
        if encoding == 'Hex':
            if data[:2].lower() == '0x':
                data = data[2:]
            data = binascii.a2b_hex(data)
        elif encoding == 'Base64':
            data = b64decode(data)
        elif encoding == 'UTF8':
            data = force_bytes(data)
        elif encoding == 'Decimal':
            logger.info(data)
            return int(data)
        else:
            data = force_bytes(data)

        data = bytes_to_long(data)
        return data

    @classmethod
    def long_2_encoding(cls, data, encoding):
        data = long_to_bytes(data)
        if encoding == 'UTF8':
            data = force_text(data)
        elif encoding == 'Hex':
            data = binascii.b2a_hex(data)
        elif encoding == 'Base64':
            data = b64encode(data)
        elif encoding == 'Decimal':
            data = bytes_to_long(data)
        else:
            data = force_text(data)

        if isinstance(data, bytes):
            data = text_type(data)[2:-1]
        return data

    def encrypt(self, plain):
        """
        :type plain long
        :param plain: 明文
        :return:
        """
        plain = self.encoding_2_long(plain, self.plain_encoding)
        rsa = RSA.construct((self.n, self.e,))
        # 最佳非对称加密填充（OAEP）
        if self.padding == 'PKCS1_OAEP':
            rsa = PKCS1_OAEP.new(rsa)
            cipher = rsa.encrypt(long_to_bytes(plain))
        elif self.padding == 'PKCS1_v1_5':
            rsa = PKCS1_v1_5.new(rsa)
            cipher = rsa.encrypt(long_to_bytes(plain))
        else:
            cipher = pow(plain, self.e, self.n)
            return self.long_2_encoding(cipher, self.cipher_encoding)

        cipher = self.long_2_encoding(bytes_to_long(cipher), self.cipher_encoding)
        return cipher

    def decrypt(self, cipher):
        """
        :type cipher long
        :param cipher: 密文
        :return:
        """
        cipher = self.encoding_2_long(cipher, self.cipher_encoding)
        if self.d is not None:
            d = self.d
        else:
            d = inverse(self.e, (self.p - 1) * (self.q - 1))

        if self.n is not None:
            n = self.n
        else:
            n = self.p * self.q

        rsa = RSA.construct((n, self.e, d))
        if self.padding == 'PKCS1_OAEP':
            rsa = PKCS1_OAEP.new(rsa)
            plain = rsa.decrypt(long_to_bytes(cipher))
        elif self.padding == 'PKCS1_v1_5':
            rsa = PKCS1_v1_5.new(rsa)
            plain = rsa.decrypt(long_to_bytes(cipher), True)
        else:
            plain = pow(cipher, d, n)
            return self.long_2_encoding(plain, self.plain_encoding)

        plain = self.long_2_encoding(bytes_to_long(plain), self.plain_encoding)
        return plain


class ZeroPadding(object):
    def __init__(self, block_size=16):
        # block size AES 固定为128位，也就是16字节
        self.bs = block_size

    def unpad(self, s):
        return s.rstrip(b'\n').rstrip(b'\x00')

    def pad(self, s):
        return s + (self.bs - len(s) % self.bs) * b'\x00'


class PKCS7Padding(object):
    """
    PKCS#5 和 PKCS#7 唯一的区别就是前者规定了数据块大小是 64 比特(8 字节)，而 AES 中数据块大小是 128 比特(16字节)，
    因此在 AES 中， PKCS#5 和 PKCS#7 没有区别。
    """

    def __init__(self, block_size=16):
        self.bs = block_size

    def pad(self, s):
        return s + (self.bs - len(s) % self.bs) * force_bytes(chr(self.bs - len(s) % self.bs))

    def unpad(self, s):
        i = s[len(s) - 1:]
        if isinstance(i, int):
            return s[:-1 * i]
        else:
            return s[:-ord(i)]


class NoPadding(object):
    def __init__(self, k=16):
        # block size AES 固定为128位，也就是16字节
        self.k = k

    def unpad(self, s):
        return s

    def pad(self, s):
        return s + (((self.k - len(s)) % self.k) * b'\x00')


class AESHelper(object):
    def __init__(self, key, iv, key_encoding, iv_encoding,
                 mode, padding, plain_encoding, cipher_encoding):
        self.key_encoding = key_encoding
        self.iv_encoding = iv_encoding
        self.mode = mode
        self.padding = padding
        self.plain_encoding = plain_encoding
        self.cipher_encoding = cipher_encoding
        self.key = key
        self.iv = iv

    def prepare(self):
        self.key = self.encoding_2_bytes(self.key, self.key_encoding)
        # len_key = len(self.key)
        # if len_key < 32:
        #     if len_key <= 16:
        #         key_padding_size = 16
        #     elif len_key <= 24:
        #         key_padding_size = 24
        #     else:
        #         key_padding_size = 32
        #     self.key += (key_padding_size - len(self.key) % key_padding_size) * b'\x00'
        # else:
        #     self.key = self.key[:32]
        self.iv = self.encoding_2_bytes(self.iv, self.iv_encoding)

    def pad(self, s, padding, bs=AES.block_size):
        if padding == 'ZeroPadding':
            return ZeroPadding(bs).pad(s)
        elif padding == 'NoPadding':
            return NoPadding(bs).pad(s)
        elif padding == 'PKCS5':
            return PKCS7Padding(bs).pad(s)
        elif padding in ('PKCS7', 'X923', 'ISO7816'):
            return pad(s, bs, padding.lower())
        else:
            return s

    def unpad(self, s, padding, bs=AES.block_size):
        if padding == 'ZeroPadding':
            return ZeroPadding(bs).unpad(s)
        elif padding == 'PKCS5':
            return PKCS7Padding(bs).unpad(s)
        elif padding in ('PKCS7', 'X923', 'ISO7816'):
            return unpad(s, bs, padding.lower())
        if padding == 'NoPadding':
            return NoPadding(bs).unpad(s)
        else:
            return s

    def encoding_2_bytes(self, data, encoding):
        if encoding == 'Hex':
            if data[:2].lower() == '0x':
                data = data[2:]
            data = binascii.a2b_hex(data)
        elif encoding == 'Base64':
            data = b64decode(data)
        elif encoding == 'UTF8':
            data = force_bytes(data)
        else:
            data = force_bytes(data)

        return data

    def bytes_2_encoding(self, data, encoding):
        if encoding == 'UTF8':
            data = force_text(data)
        elif encoding == 'Hex':
            data = binascii.b2a_hex(data)
        elif encoding == 'Base64':
            data = b64encode(data)
        else:
            data = force_text(data)

        if isinstance(data, bytes):
            data = text_type(data)[2:-1]
        return data

    def decrypt(self, cipher):
        self.prepare()

        aes = None
        if self.mode == 'ECB':
            aes = AES.new(self.key, AES.MODE_ECB)
        elif self.mode == 'CBC':
            aes = AES.new(self.key, AES.MODE_CBC, self.iv)
        elif self.mode == 'CFB':
            aes = AES.new(self.key, AES.MODE_CFB, self.iv)
        elif self.mode == 'OFB':
            aes = AES.new(self.key, AES.MODE_OFB, self.iv)
        elif self.mode == 'CTR':
            aes = AES.new(self.key, AES.MODE_CTR, self.iv)

        if aes is None:
            plain = b''
        else:
            cipher = self.encoding_2_bytes(cipher, self.cipher_encoding)
            plain = aes.decrypt(cipher)
            plain = self.unpad(plain, self.padding)
        return self.bytes_2_encoding(plain, self.plain_encoding)

    def encrypt(self, plain):
        self.prepare()

        aes = None
        if self.mode == 'ECB':
            aes = AES.new(self.key, AES.MODE_ECB)
        elif self.mode == 'CBC':
            aes = AES.new(self.key, AES.MODE_CBC, self.iv)
        elif self.mode == 'CFB':
            aes = AES.new(self.key, AES.MODE_CFB, self.iv)
        elif self.mode == 'OFB':
            aes = AES.new(self.key, AES.MODE_OFB, self.iv)
        elif self.mode == 'CTR':
            aes = AES.new(self.key, AES.MODE_CTR, self.iv)

        if aes is None:
            cipher = b''
        else:
            plain = self.encoding_2_bytes(plain, self.plain_encoding)
            plain_len = len(plain)
            if self.padding == 'NoPadding':
                plain = self.pad(plain, self.padding)
                cipher = aes.encrypt(plain)
                cipher = cipher[:plain_len]
            else:
                plain = self.pad(plain, self.padding)
                cipher = aes.encrypt(plain)
        return self.bytes_2_encoding(cipher, self.cipher_encoding)


def main():
    pass
    # key = '3ae383e2163dd44270284f1554d9be8d'.decode('hex')
    # key = 'Anaconda'
    # cipher_file = 'cipher'
    # with open(cipher_file, 'rb') as f:
    #     data = f.read()
    #     print data.encode('hex')
    #
    # import base64
    # print base64.b64encode(data)
    # AESHelper(key, cipher_file).decrypt_ecb(data)
