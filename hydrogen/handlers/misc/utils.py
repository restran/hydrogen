# -*- coding: utf-8 -*-
# Created by restran on 2018/8/1
from __future__ import unicode_literals, absolute_import

import base64
import socket
import struct
from collections import Counter
from mountains import force_bytes, force_text
from future.moves.urllib.parse import unquote
from mountains.http import query_str_2_dict
from mountains.utils import PrintCollector


class IPConverter(object):
    @classmethod
    def ip2int(cls, ip, *args, **kwargs):
        # ip address to int
        return socket.ntohl(struct.unpack("I", socket.inet_aton(str(ip)))[0])

    @classmethod
    def int2ip(cls, int_ip, *args, **kwargs):
        # int to ip address
        int_ip = int(int_ip)
        return socket.inet_ntoa(struct.pack('I', socket.htonl(int_ip)))


def remove_duplicated(data, *args, **kwargs):
    """
    一行一个数据去重
    """
    data_list = data.splitlines()
    new_data = []
    data_dict = {}
    for t in data_list:
        if t not in data_dict:
            new_data.append(t)
            data_dict[t] = None

    return '\n'.join(new_data)


def char_count(data, *args, **kwargs):
    """
    字符频率统计
    """
    p = PrintCollector()
    r = Counter(data)
    length = len(data)
    data = [{'k': k, 'v': v} for k, v in r.items()]
    data1 = sorted(data, key=lambda a: a['v'], reverse=False)
    p.print('从小到大: ')
    for t in data1:
        k, v = t['k'], t['v']
        p.print('{}: {:.1f}%, {}'.format(k, v / length * 100, v))

    data2 = sorted(data, key=lambda a: a['v'], reverse=True)
    p.print('')
    p.print('从大到小: ')
    for t in data2:
        k, v = t['k'], t['v']
        p.print('{}: {:.1f}%, {}'.format(k, v / length * 100, v))

    return p.smart_output()


def caidao_decode(data, *args, **kwargs):
    p = PrintCollector()
    data_dict = query_str_2_dict(data.strip())
    d = {}
    for k, v in data_dict.items():
        v = unquote(v)
        try:
            x = force_bytes(v)
            missing_padding = len(v) % 4
            if missing_padding != 0:
                x += b'=' * (4 - missing_padding)

            d[k] = force_text(base64.decodebytes(x))
        except Exception as e:
            print(e)
            d[k] = v

    z0_raw = ''
    if 'z0' in d:
        z0_raw = d['z0']
        d['z0'] = ';\n'.join(d['z0'].split(';'))

    for k, v in d.items():
        value = '{}:\n{}\n'.format(k, v)
        p.print(value)
        if k == 'z0':
            if value != 'z0:\n{}\n'.format(z0_raw):
                p.print('z0_raw:\n{}\n'.format(z0_raw))

    return p.smart_output()
