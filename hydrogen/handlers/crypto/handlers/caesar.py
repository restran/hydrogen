# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from mountains.utils import PrintCollector

"""
破解凯撒密码python脚本
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
        r = decode(data, key)
        p.print(r)
    return p.smart_output(verbose=verbose)


def main():
    s = 'tedr{ykdd_dyckl_xvpdfyy3sbve8_c7l0f}'
    decode_all(s)

    s = 'flag{abcdefg}'
    data = []
    for i, x in enumerate(s):
        x = encode(x, i+1)
        data.append(x)
    print(''.join(data))


if __name__ == '__main__':
    main()
