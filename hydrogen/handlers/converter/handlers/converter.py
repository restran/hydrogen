# -*- coding: utf-8 -*-
"""
Created on 2017/9/14
"""

from __future__ import unicode_literals, absolute_import

import base64
import binascii
import string
from base64 import b64decode, b32decode, b16decode, urlsafe_b64encode, urlsafe_b64decode
from xml.sax.saxutils import escape as xml_escape_func
from xml.sax.saxutils import unescape as xml_unescape_func
from handlers.converter.handlers.base58 import b58decode, b58encode
from handlers.converter.handlers.base92 import b92decode, b92encode
from handlers.converter.handlers.base91 import b91decode, b91encode
from handlers.converter.handlers.base100 import b100decode, b100encode
from handlers.converter.handlers.base62 import b62encode, b62decode
from handlers.converter.handlers.base36 import b36decode, b36encode
from handlers.converter.handlers.any_base32 import any_b32decode, any_b32encode
from base64 import b85decode, a85decode
from mountains.encoding import force_bytes, force_text


def base_padding(data, length=4):
    data = force_bytes(data)
    if len(data) % length != 0:
        data = data + b'=' * (length - len(data) % length)

    return data


def partial_decode(decode_method, data, base_padding_length=4):
    """
    对前面可以解码的数据一直解到无法解码
    :param base_padding_length:
    :param decode_method:
    :param data:
    :return:
    """
    data = force_bytes(data)
    result = []
    while len(data) > 0:
        tmp = base_padding(data[:base_padding_length], base_padding_length)
        data = data[base_padding_length:]
        try:
            r = decode_method(tmp)
            result.append(r)
        except:
            break
    return b''.join(result)


def partial_base64_decode(data):
    return partial_decode(b64decode, data, 4)


def partial_base32_decode(data):
    return partial_decode(b32decode, data, 8)


def partial_base16_decode(data):
    return partial_decode(b16decode, data, 2)


def url_safe_b64encode(data):
    return force_text(urlsafe_b64encode(force_bytes(data)))


def url_safe_b64decode(data):
    return force_text(urlsafe_b64decode(force_bytes(data)))


def from_base85(data):
    return force_text(base64.b85decode(force_bytes(data)))


def to_base85(data):
    return force_text(base64.b85encode(force_bytes(data)))


def from_ascii85(data):
    return force_text(base64.a85decode(force_bytes(data)))


def to_ascii85(data):
    return force_text(base64.a85encode(force_bytes(data)))


def from_base92(data):
    return force_text(b92decode(data))


def to_base92(data):
    return force_text(b92encode(force_bytes(data)))


def from_base91(data):
    return b91decode(data).decode()


def to_base91(data):
    return force_text(b91encode(force_bytes(data)))


def from_base100(data):
    return b100decode(data).decode()


def to_base100(data):
    return force_text(b100encode(force_bytes(data)))


def from_base62(data):
    return str(b62decode(data))


def to_base62(data):
    return force_text(b62encode(int(data)))


def from_any_base32(data):
    return any_b32decode(force_bytes(data)).decode()


def to_any_base32(data):
    return force_text(any_b32encode(force_bytes(data)))


def from_base36(data):
    return str(b36decode(data))


def to_base36(data):
    return force_text(b36encode(int(data)))


def to_base64(data):
    """
    把字符串转换成BASE64编码
    :param data: 字符串
    :return: BASE64字符串
    """
    return base64.b64encode(force_bytes(data))


def from_base64(data):
    """
    解base64编码
    :param data: base64字符串
    :return: 字符串
    """
    data = base_padding(data, 4)
    try:
        r = base64.b64decode(data)
    except:
        r = partial_base64_decode(data)
    return r


def to_base32(data):
    """
    把字符串转换成BASE32编码，5个ASCII字符一组，生成8个Base字符
    :param data: 字符串
    :return: BASE32字符串
    """
    return base64.b32encode(force_bytes(data))


def from_base32(data):
    """
    解base32编码，5个ASCII字符一组，生成8个Base字符
    :param data: base32字符串
    :return: 字符串
    """
    data = base_padding(data, 8)
    try:
        r = base64.b32decode(data)
    except:
        r = partial_base32_decode(data)
    return r


def to_base16(data):
    """
    把字符串转换成BASE16编码
    :param data: 字符串
    :return: BASE16字符串
    """
    return base64.b16encode(force_bytes(data))


def from_base16(data):
    """
    解base16编码
    :param data: base16字符串
    :return: 字符串
    """
    return base64.b16decode(data)


def from_base58(data):
    return b58decode(force_bytes(data))


def to_base58(data):
    return b58encode(force_bytes(data))


def to_uu(data):
    """
    uu编码
    :param data: 字符串
    :return: 编码后的字符串
    """
    r = binascii.b2a_uu(force_bytes(data))
    return force_text(r)


def from_uu(data):
    """
    解uu编码
    :param data: uu编码的字符串
    :return: 字符串
    """
    r = binascii.a2b_uu(data)
    return force_text(r)


def str2hex(s):
    """
    把一个字符串转成其ASCII码的16进制表示
    :param s: 要转换的字符串
    :return: ASCII码的16进制表示字符串
    """
    return force_text(binascii.b2a_hex(force_bytes(s)))


def swap_case(s):
    new_data = []
    for t in s:
        if t in string.ascii_lowercase:
            t = t.upper()
        elif t in string.ascii_uppercase:
            t = t.lower()

        new_data.append(t)
    return ''.join(new_data)


def hex2str(s):
    """
    把十六进制字符串转换成其ASCII表示字符串
    :param s: 十六进制字符串
    :return: 字符串
    """
    if s[:2].lower() == '0x':
        s = s[2:]
    return binascii.a2b_hex(s)


base = [str(x) for x in range(10)] + [chr(x) for x in range(ord('A'), ord('A') + 6)]


def b642hex(s):
    s = base_padding(s, 4)
    s = b64decode(force_bytes(s))
    return str2hex(s)


def hex2b64(s):
    s = hex2str(s)
    return to_base64(s)


# bin2dec
# 二进制 to 十进制: int(str,n=10)
def bin2dec(s):
    return str(int(s, 2))


# dec2bin
# 十进制 to 二进制: bin()
def dec2bin(s):
    num = int(s)
    mid = []
    while True:
        if num == 0:
            break
        num, rem = divmod(num, 2)
        mid.append(base[rem])

    return ''.join([str(x) for x in mid[::-1]])


# hex2dec
# 十六进制 to 十进制
def hex2dec(s):
    return str(int(s.upper(), 16))


# dec2hex
# 十进制 to 八进制: oct()
# 十进制 to 十六进制: hex()
def dec2hex(s):
    num = int(s)
    mid = []
    while True:
        if num == 0:
            break
        num, rem = divmod(num, 16)
        mid.append(base[rem])

    r = ''.join([str(x) for x in mid[::-1]])
    if len(r) % 2 != 0:
        r = '0' + r

    return r


# hex2tobin
# 十六进制 to 二进制: bin(int(str,16))
def hex2bin(s):
    if len(s) % 2 != 0:
        s = '0' + s

    result = []
    for i in range(len(s) // 2):
        t = s[i * 2:(i + 1) * 2]
        x = dec2bin(hex2dec(t.upper()))
        padding_length = (8 - len(x) % 8) % 8
        # 每个16进制值（2个字符）进行转码，不足8个的，在前面补0
        x = '%s%s' % ('0' * padding_length, x)
        result.append(x)

    result = ''.join(result)
    return result if result != '' else '00000000'


# bin2hex
# 二进制 to 十六进制: hex(int(str,2))
def bin2hex(s):
    padding_length = (8 - len(s) % 8) % 8
    # 从前往后解码，不足8个的，在后面补0
    encode_str = '%s%s' % (s, '0' * padding_length)
    # 解码后是 0xab1234，需要去掉前面的 0x
    return hex(int(encode_str, 2))[2:].rstrip('L')


def str2dec(s):
    """
    string to decimal number.
    """
    if not len(s):
        return 0
    return int(str2hex(s), 16)


def dec2str(n):
    """
    decimal number to string.
    """
    s = hex(int(n))[2:].rstrip('L')
    if len(s) % 2 != 0:
        s = '0' + s
    return force_text(hex2str(s))


def str2bin(s):
    """
    String to binary.
    """
    ret = []
    for c in s:
        ret.append(bin(ord(c))[2:].zfill(8))
    return ''.join(ret)


def bin2str(b):
    """
    Binary to string.
    """
    ret = []
    for pos in range(0, len(b), 8):
        ret.append(chr(int(b[pos:pos + 8], 2)))
    return ''.join(ret)


def from_digital(s, num):
    """
    进制转换，从指定机制转到10进制
    :param s:
    :param num:
    :return:
    """
    if not 1 < num < 10:
        raise ValueError('digital num must between 1 and 10')
    return '%s' % int(s, num)


def to_digital(d, num):
    """
    进制转换，从10进制转到指定机制
    :param d:
    :param num:
    :return:
    """
    if not isinstance(num, int) or not 1 < num < 10:
        raise ValueError('digital num must between 1 and 10')

    d = int(d)
    result = []
    x = d % num
    d = d - x
    result.append(str(x))
    while d > 0:
        d = d // num
        x = d % num
        d = d - x
        result.append(str(x))
    return ''.join(result[::-1])


def all_digit_convert(data, data_type):
    if data_type == 'binary':
        decimal = bin2dec(data)
    elif data_type == 'octal':
        decimal = from_digital(data, 8)
    elif data_type == 'decimal':
        decimal = int(data)
    elif data_type == 'hex':
        decimal = hex2dec(data)
    elif data_type == 'ascii':
        decimal = str2dec(data)
    else:
        return {}

    data = {
        'hex': dec2hex(decimal),
        'decimal': decimal,
        'octal': to_digital(decimal, 8),
        'binary': dec2bin(decimal),
        'ascii': dec2str(decimal)
    }

    return data


def xml_escape(data):
    return xml_escape_func(data)


def xml_un_escape(data):
    return xml_unescape_func(data)


if __name__ == "__main__":
    # x = to_digital(7, 3)
    # print(x)
    x = 'JVDFER2HHU6T2==='
    x = partial_base32_decode(x)
    x = hex2str('20B4')
    print(x)
