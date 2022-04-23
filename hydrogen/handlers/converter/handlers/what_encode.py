# -*- coding: utf-8 -*-
# Created by restran on 2017/11/4
from __future__ import unicode_literals, absolute_import

import base64
import hashlib
import logging
import re
import string
import zlib
from base64 import urlsafe_b64decode
from copy import deepcopy
from functools import cmp_to_key
from optparse import OptionParser

from future.moves.urllib.parse import unquote_plus
from mountains import PY3, PY2
from mountains.encoding import force_text, force_bytes
from .base91 import b91decode
from .base92 import b92decode
from handlers.converter.handlers.converter import partial_base16_decode, base_padding, hex2str, from_base58
from handlers.crypto.handlers.rot13 import decode_rot13

logger = logging.getLogger(__name__)

if PY3:
    from base64 import b85decode, a85decode

"""
自动解析字符串数据是采用了怎样的编码
如果因为数据太多，导致在命令行上面看不全的话，可以使用 
python what_encode.py -f input.txt > out.txt
"""

# 自动尝试这些编码
encode_methods = [
    'hex',
    'base64',
    'urlsafe_b64',
    'base32',
    'base16',  # base16 其实就是16进制
    'ascii_85',  # ascii85
    'base85',  # base85
    'base58',  # base58
    'base91',  # base91
    'base92',  # base92
    'binary',  # 01010101
    'octal',  # 八进制
    'octal_binary',  # 八进制直接转成16进制的二进制格式
    # 八进制数字的 ascii 字符串，153, 134, 171, 173, 64
    'octal_ascii',
    # 十进制数字的 ascii 字符串
    'decimal_ascii',
    'decimal',  # 10 进制数据，转成16进制
    'zlib',
    'rot13',
    'pawn_shop',  # 当铺密码
    'swap_case',  # 大小写交换
    'reverse_alphabet',  # 字母表逆序
    'reverse',  # 逆序
    'urlencode',
]

parser = OptionParser()
parser.add_option("-d", "--data str", dest="data_str", type="string",
                  help="data str")
parser.add_option("-D", "--max_depth", dest="max_depth", type="int",
                  default=10, help="max depth")
parser.add_option("-f", "--file name", dest="file_name", type="string",
                  help="read from file")
parser.add_option("-s", "--save file name", dest="save_file_name", type="string",
                  help="save decoded data to file")
parser.add_option("-m", "--decode method list", dest="method_list", type="string",
                  help="decode method list, base64->hex")
parser.add_option("-x", "--only_printable", dest="only_printable", default=True,
                  action="store_false", help="disable only printable output")
parser.add_option("-v", "--verbose", dest="verbose", default=False,
                  action="store_true", help="verbose")


class WhatEncode(object):
    def __init__(self, data_str, method_list=None, file_name=None,
                 save_file_name=None, only_printable=False,
                 printable_percent=.75, max_depth=10, verbose=False):
        """

        :param data_str:
        :param method_list:
        :param file_name:
        :param save_file_name:
        :param only_printable:
        :param printable_percent: 可打印字符至少要占百分之多少
        :param verbose:
        """
        self.data_str = data_str
        self.method_list = method_list
        self.file_name = file_name
        self.save_file_name = save_file_name
        self.only_printable = only_printable
        self.printable_percent = printable_percent
        self.verbose = verbose
        self.max_depth = max_depth
        # 上一个解码结果为可打印字符
        self.last_result_printable = True

        if self.file_name is not None:
            with open(self.file_name, 'rb') as f:
                self.data_str = f.read()

    @classmethod
    def regex_match(cls, regex, encode_str):
        try:
            return regex.match(force_text(encode_str))
        except:
            print(encode_str)
            return False

    def parse_str(self, encode_str, decode_method, m_list):
        if len(m_list) > self.max_depth:
            return False, encode_str

        # encode_str = deepcopy(encode_str)
        encode_str = force_bytes(encode_str)
        if decode_method in ['zlib']:
            encode_str = force_bytes(encode_str)
        else:
            encode_str = force_text(encode_str)

        raw_encode_str = deepcopy(encode_str)
        if len(encode_str) <= 0:
            return False, raw_encode_str

        try:
            if decode_method == 'base16':
                # 避免无限递归
                # base_list = ('base16', 'base32', 'base64', 'urlsafe_b64')
                # base_list = ()
                if len(encode_str) < 4:
                    return False, raw_encode_str

                encode_str = encode_str.upper()
                rex = re.compile('^[0-9A-F]+[=]*$', re.MULTILINE)
                if self.regex_match(rex, encode_str):
                    decode_str = partial_base16_decode(encode_str)
                else:
                    return False, raw_encode_str
            elif decode_method == 'base32':
                encode_str = encode_str.strip().replace(' ', '').replace('\n', '')
                # 避免无限递归
                # base_list = ('base16', 'base32', 'base64', 'urlsafe_b64')
                # base_list = ()
                if len(encode_str) < 4:
                    return False, raw_encode_str

                encode_str = encode_str.upper()
                rex = re.compile('^[A-Z2-7=]+$', re.MULTILINE)
                # 自动纠正填充
                if self.regex_match(rex, encode_str):
                    decode_str = base64.b32decode(base_padding(encode_str, 8))
                else:
                    return False, raw_encode_str
            elif decode_method == 'base64':
                encode_str = encode_str.strip().replace(' ', '').replace('\n', '')

                # 避免无限递归
                # base_list = ('base16', 'base32', 'base64', 'urlsafe_b64')
                # base_list = ()
                if len(encode_str) < 4:
                    return False, raw_encode_str

                rex = re.compile('^[A-Za-z0-9+/=]+$', re.MULTILINE)
                # 自动纠正填充
                if self.regex_match(rex, encode_str):
                    decode_str = base64.b64decode(base_padding(encode_str, 4))
                else:
                    return False, raw_encode_str
            elif decode_method == 'urlsafe_b64':
                encode_str = encode_str.strip().replace(' ', '').replace('\n', '')
                # base_list = ('base16', 'base32', 'base64', 'urlsafe_b64')
                # base_list = ()
                if len(encode_str) < 4:
                    return False, raw_encode_str
                rex = re.compile('^[A-Za-z0-9-_=]+$', re.MULTILINE)
                # 自动纠正填充
                if self.regex_match(rex, encode_str):
                    decode_str = urlsafe_b64decode(base_padding(encode_str, 4))
                else:
                    return False, raw_encode_str
            elif decode_method == 'base58':
                encode_str = encode_str.strip().replace(' ', '').replace('\n', '')
                if len(encode_str) < 4:
                    return False, raw_encode_str

                rex = re.compile('^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]+$', re.MULTILINE)
                # 自动纠正填充
                if self.regex_match(rex, encode_str):
                    decode_str = from_base58(encode_str)
                else:
                    return False, raw_encode_str
            elif decode_method == 'base91':
                encode_str = encode_str.strip().replace(' ', '').replace('\n', '')
                if len(encode_str) < 4:
                    return False, raw_encode_str
                decode_str = b91decode(encode_str)
            elif decode_method == 'base92':
                encode_str = encode_str.strip().replace(' ', '').replace('\n', '')
                if len(encode_str) < 4:
                    return False, raw_encode_str
                decode_str = b92decode(encode_str)
            elif decode_method == 'ascii_85':
                if len(encode_str) < 4:
                    return False, raw_encode_str

                if PY2:
                    return False, raw_encode_str

                try:
                    decode_str = a85decode(force_bytes(encode_str))
                    return True, decode_str
                except:
                    return False, encode_str
            elif decode_method == 'base85':
                if len(encode_str) < 4:
                    return False, raw_encode_str

                if PY2:
                    return False, raw_encode_str

                try:
                    decode_str = b85decode(force_bytes(encode_str))
                    return True, decode_str
                except:
                    return False, encode_str
            elif decode_method == 'rot13':
                # 如果这里不做限制，会无限递归下去
                if 'rot13' in m_list:
                    return False, raw_encode_str
                decode_str = decode_rot13(encode_str)
            elif decode_method == 'pawn_shop':
                try:
                    encode_str = encode_str.decode('gb2312')
                except:
                    pass

                encode_str = force_text(encode_str)
                encode_str = encode_str.replace(' ', '').strip()
                code_base = '口由中人工大王夫井羊'
                decode_str = []
                for t in encode_str:
                    if t in code_base:
                        i = code_base.index(t)
                        decode_str.append(str(i))
                    else:
                        return False, raw_encode_str
                decode_str = ''.join(decode_str)

                if len(decode_str) < 0:
                    return False, raw_encode_str
            elif decode_method == 'decimal':
                if len(encode_str) < 4:
                    return False, raw_encode_str

                rex = re.compile('^[0-9]+$', re.MULTILINE)
                if not self.regex_match(rex, encode_str):
                    return False, raw_encode_str
                # 解码后是 0xab1234，需要去掉前面的 0x
                decode_str = hex(int(encode_str))[2:].rstrip('L')
            elif decode_method == 'binary':
                rex = re.compile('^[0-1]+$', re.MULTILINE)
                if not self.regex_match(rex, encode_str):
                    return False, raw_encode_str

                # 不足8个的，在后面填充0
                padding_length = (8 - len(encode_str) % 8) % 8
                encode_str = '%s%s' % (encode_str, '0' * padding_length)
                # 解码后是 0xab1234，需要去掉前面的 0x
                decode_str = hex(int(encode_str, 2))[2:].rstrip('L')
            elif decode_method in ['octal', 'octal_ascii', 'octal_binary']:
                # 8进制转成16进制的数据
                rex = re.compile('^[0-7]+$', re.MULTILINE)
                if not self.regex_match(rex, encode_str):
                    return False, raw_encode_str

                rex = re.compile('^[0-1]+$', re.MULTILINE)
                if self.regex_match(rex, encode_str):
                    return False, raw_encode_str

                if len(encode_str) < 4:
                    return False, raw_encode_str

                if decode_method == 'octal':
                    # 解码后是 0xab1234，需要去掉前面的 0x
                    decode_str = hex(int(encode_str, 8))[2:].rstrip('L')
                elif decode_method == 'octal_ascii':
                    encode_str = encode_str.replace(' ', '').strip()
                    # 8 进制的 177 转成十进制后是 128
                    tmp_list = list(encode_str)
                    ascii_list = []
                    while len(tmp_list) > 0:
                        tmp_str = ''.join(tmp_list[:3])
                        if int(tmp_str, 8) > 127:
                            tmp_str = ''.join(tmp_list[:2])
                            tmp_list = tmp_list[2:]
                        else:
                            tmp_list = tmp_list[3:]
                        ascii_list.append(chr(int(tmp_str, 8)))
                    decode_str = ''.join(ascii_list)
                elif decode_method == 'octal_binary':
                    # 因为这里有补0的操作，要避免无限递归
                    if len(m_list) > 0 and \
                            (m_list[-1] in ('octal_binary', 'octal', 'binary')
                             or len(encode_str) < 8):
                        return False, raw_encode_str

                    # 将8进制直接转成16进制，也就是3个8进制数字转成2个16进制字符
                    # 先将每个8进制数字转成二进制，不足3个的前面补0
                    encode_str = encode_str.replace(' ', '').strip()
                    tmp_bin_list = ['%03d' % int(bin(int(t))[2:]) for t in list(encode_str)]
                    tmp_bin_list = [t for t in tmp_bin_list]
                    # logger.info(tmp_bin_list)
                    decode_str = ''.join(tmp_bin_list)
                else:
                    return False, raw_encode_str
            elif decode_method == 'decimal_ascii':
                if len(encode_str) < 4:
                    return False, raw_encode_str

                encode_str = encode_str.replace(' ', '').strip()
                rex = re.compile('^[0-9]+$', re.MULTILINE)
                if not self.regex_match(rex, encode_str):
                    return False, raw_encode_str

                # ascii 字符串，10进制最大127
                tmp_list = list(encode_str)
                ascii_list = []
                while len(tmp_list) > 0:
                    tmp_str = ''.join(tmp_list[:3])
                    if int(tmp_str) > 127:
                        tmp_str = ''.join(tmp_list[:2])
                        tmp_list = tmp_list[2:]
                    else:
                        tmp_list = tmp_list[3:]
                    ascii_list.append(chr(int(tmp_str)))
                decode_str = ''.join(ascii_list)
            elif decode_method in ['swap_case', 'reverse_alphabet', 'reverse']:
                # 如果这里不做限制，会无限递归下去
                if len(m_list) > 0:
                    for t in ['swap_case', 'reverse_alphabet', 'reverse']:
                        if t in m_list:
                            return False, raw_encode_str

                # 一定要包含 ascii 字符
                tmp_data = [t for t in encode_str if t in string.ascii_letters]
                if len(tmp_data) <= 0:
                    return False, raw_encode_str

                # rex = re.compile('^[A-Za-z0-9+/=]$', re.MULTILINE)
                # if not self.regex_match(rex, encode_str):
                #     return False, raw_encode_str

                if decode_method == 'swap_case':
                    new_data = []
                    for t in encode_str:
                        if t in string.ascii_lowercase:
                            t = t.upper()
                        elif t in string.ascii_uppercase:
                            t = t.lower()
                        new_data.append(t)
                    decode_str = ''.join(new_data)
                elif decode_method == 'reverse_alphabet':
                    # 字母逆序，a->z, z->a
                    new_data = []
                    for t in encode_str:
                        if t in string.ascii_letters:
                            if t in string.ascii_lowercase:
                                t = ord(t) + (25 - (ord(t) - ord('a')) * 2)
                                t = chr(t)
                            else:
                                t = ord(t) + (25 - (ord(t) - ord('A')) * 2)
                                t = chr(t)
                        new_data.append(t)
                    decode_str = ''.join(new_data)
                elif decode_method == 'reverse':
                    # 逆序
                    decode_str = encode_str[::-1]
                else:
                    return False, raw_encode_str
            elif decode_method == 'urlencode':
                if len(encode_str) < 4:
                    return False, raw_encode_str

                decode_str = unquote_plus(encode_str)
            elif decode_method == 'hex':
                if len(encode_str) < 4:
                    return False, raw_encode_str

                encode_str = encode_str.lower()
                rex = re.compile('^[a-f0-9]+$', re.MULTILINE)
                if self.regex_match(rex, encode_str.lower()):
                    # 修正基数位数的16进制数据
                    if len(encode_str) % 2 != 0:
                        encode_str += '0'

                    decode_str = force_text(hex2str(encode_str))
                else:
                    return False, raw_encode_str
            elif decode_method == 'zlib':
                if len(encode_str) < 4:
                    return False, raw_encode_str

                try:
                    decode_str = zlib.decompress(force_bytes(encode_str))
                    if self.calc_printable_percent(decode_str) < self.printable_percent:
                        return False, raw_encode_str

                except:
                    return False, raw_encode_str
            else:
                decode_str = encode_str.decode(decode_method)

            if len(decode_str) <= 0:
                return False, raw_encode_str
            elif force_bytes(encode_str) == force_bytes(decode_str):
                return False, raw_encode_str
            else:
                # 解码的内容只有可打印字符，才认为合法
                if self.only_printable:
                    printable_percent = 1.0
                else:
                    printable_percent = self.printable_percent

                is_printable = True
                # 如果可打印字符低于一定的百分比，就认为解码失败
                if self.calc_printable_percent(decode_str) < printable_percent:
                    is_printable = False

                if is_printable is False:
                    if self.last_result_printable is False:
                        return False, raw_encode_str

                self.last_result_printable = is_printable

                return True, decode_str
        except Exception as e:
            if self.verbose:
                logger.exception(e)
            return False, raw_encode_str

    def calc_printable_percent(self, data):
        tmp_decode_str = list(data)
        if len(tmp_decode_str) <= 0:
            return 0
        printable_count = 0
        for t in tmp_decode_str:
            if isinstance(t, int):
                t = chr(t)
            else:
                t = str(t)
            if t in string.printable:
                printable_count += 1

        x = printable_count * 1.0 / len(tmp_decode_str)
        print(x)
        print(data)
        return x

    def parse(self):
        encode_str = self.data_str
        encode_str = encode_str.strip()
        should_try_list = []
        # 先进行第一层解密
        for m in encode_methods:
            success, decode_str = self.parse_str(encode_str, m, [])
            if success:
                should_try_list.append({'data': decode_str, 'm_list': [m]})

        result_method_dict = {}
        while len(should_try_list) > 0:
            new_should_try_list = []
            for item in should_try_list:
                m_list = item['m_list']
                data = item['data']
                has_print = False
                for i, m in enumerate(encode_methods):
                    tmp_m_list = deepcopy(m_list)
                    self.last_result_printable = True
                    success, decode_str = self.parse_str(data, m, tmp_m_list)

                    if success:
                        tmp_m_list.append(m)
                        if tmp_m_list not in new_should_try_list:
                            new_should_try_list.append({
                                'data': decode_str,
                                'm_list': tmp_m_list
                            })
                    else:
                        if len(tmp_m_list) > 0 and not has_print:
                            has_print = True
                            md5 = hashlib.md5(force_bytes(decode_str)).hexdigest()
                            if md5 in result_method_dict:
                                item = result_method_dict[md5]
                                # 为了避免数据很繁杂，只保留最短路径
                                if len(item['m_list']) > len(tmp_m_list):
                                    item['m_list'] = tmp_m_list
                                    item['methods'] = '->'.join(tmp_m_list)
                            else:
                                if self.calc_printable_percent(decode_str) >= self.printable_percent:
                                    result_method_dict[md5] = {
                                        'data': '%s' % decode_str,
                                        'm_list': tmp_m_list,
                                        'methods': '->'.join(tmp_m_list)
                                    }

            should_try_list = new_should_try_list

        def cmp_method_list(x, y):
            # 按照解码后的数据长度排序，最小的排在前面
            len_x = len(x['data'])
            len_y = len(y['data'])
            if len_x == len_y:
                for index, t in enumerate(x['m_list']):
                    if x['m_list'][index] > y['m_list'][index]:
                        return 1
                    elif x['m_list'][index] == y['m_list'][index]:
                        pass
                    else:
                        return -1
                return 0
            elif len_x > len_y:
                return -1
            else:
                return 1

            # 按使用方法列表的长度排序，最大的排在前面
            # len_x = len(x['m_list'])
            # len_y = len(y['m_list'])
            # if len_x == len_y:
            #     for index, t in enumerate(x['m_list']):
            #         if x['m_list'][index] > y['m_list'][index]:
            #             return 1
            #         elif x['m_list'][index] == y['m_list'][index]:
            #             pass
            #         else:
            #             return -1
            #     return 0
            # elif len_x > len_y:
            #     return 1
            # else:
            #     return -1

        result_method_list = sorted(result_method_dict.values(),
                                    key=cmp_to_key(lambda x, y: cmp_method_list(x, y)),
                                    reverse=True)
        return result_method_list


def decode(data_str, max_depth):
    if data_str in ('', None):
        return []

    p = WhatEncode(data_str=data_str, only_printable=True,
                   max_depth=max_depth, verbose=False)
    return p.parse()
