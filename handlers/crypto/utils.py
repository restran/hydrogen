# -*- coding: utf-8 -*-
# created by restran on 2018/05/18
from __future__ import unicode_literals, absolute_import
from Cryptodome.PublicKey import RSA
from Cryptodome.Util.number import inverse
from ..converter.handlers.converter import hex2dec


def read_rsa_pem_key(key_content):
    n, e, p, q = '', '', '', ''

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


def ensure_long(c):
    if not isinstance(c, int):
        if len(c) == 0:
            return 0
        if c.lower().startswith('0x'):
            return int(hex2dec(c[2:]))
        else:
            return int(c)
    return c


def make_private_key_pem(n, e, p, q):
    n, e, p, q = ensure_long(n), ensure_long(e), ensure_long(p), ensure_long(q)
    d = inverse(e, (p - 1) * (q - 1))
    rsa = RSA.construct((n, e, d))
    return rsa.exportKey()


def make_public_key_pem(n, e):
    n, e = ensure_long(n), ensure_long(e)
    rsa = RSA.construct((n, e,))
    return rsa.publickey().exportKey()


def rsa_encrypt(plain, n, e):
    """
    :type plain long
    :param plain: 明文
    :param n:
    :param e:
    :return:
    """
    plain, n, e = ensure_long(plain), ensure_long(n), ensure_long(e)
    cipher = pow(plain, e, n)
    return cipher


def rsa_decrypt(cipher, e, p, q):
    """
    :param q:
    :param p:
    :param e:
    :type cipher long
    :param cipher: 密文
    :return:
    """
    cipher, e, p, q = ensure_long(cipher), ensure_long(e), ensure_long(p), ensure_long(q)
    d = inverse(e, (p - 1) * (q - 1))
    n = p * q
    plain = pow(cipher, d, n)
    return plain
