# -*- coding: utf-8 -*-
# Created by restran on 2017/11/3
from __future__ import unicode_literals, absolute_import
import string

"""
埃特巴什码
"""


def decode(data, verbose=False):
    # 字母逆序，a->z, z->a
    new_data = []
    for t in data:
        if t in string.ascii_letters:
            if t in string.ascii_lowercase:
                t = ord(t) + (25 - (ord(t) - ord('a')) * 2)
                t = chr(t)
            else:
                t = ord(t) + (25 - (ord(t) - ord('A')) * 2)
                t = chr(t)
        new_data.append(t)
    decode_str = ''.join(new_data)
    return decode_str
