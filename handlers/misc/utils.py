# -*- coding: utf-8 -*-
# Created by restran on 2018/8/1
from __future__ import unicode_literals, absolute_import
import socket
import struct
from mountains.utils import PrintCollector
from collections import Counter

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
