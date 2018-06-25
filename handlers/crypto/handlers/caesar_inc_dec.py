# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from mountains.utils import PrintCollector

"""
递增递减凯撒密码python脚本
每个字符的偏移是不同的，递增偏移
"""


def convert(c, key, start='a', n=26):
    a = ord(start)
    offset = ((ord(c) - a + key) % n)
    return chr(a + offset)


def encode(s, key):
    o = ""
    for c in s:
        if c.islower():
            o += convert(c, key, 'a')
        elif c.isupper():
            o += convert(c, key, 'A')
        else:
            o += c
    return o


def decode(s, key):
    return encode(s, -key)


def decode_all(data, verbose=True):
    p = PrintCollector()
    for key in range(26):
        d = []
        for i, t in enumerate(data):
            k = (key + i) % 26
            r = decode(t, k)
            d.append(r)
        p.print(''.join(d))

    p.print('')
    for key in range(26):
        d = []
        for i, t in enumerate(data):
            k = (key + i) % 26
            r = encode(t, k)
            d.append(r)
        p.print(''.join(d))

    return p.smart_output(verbose=verbose)


def main():
    s = 'tedr{ykdd_dyckl_xvpdfyy3sbve8_c7l0f}'
    decode_all(s)

    s = 'gndk{gikmoqs}'
    decode_all(s)


if __name__ == '__main__':
    main()
