# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from mountains.utils import PrintCollector

"""
递增递减凯撒密码，实现 33-126 ASCII 可打印的字符循环平移
每个字符的偏移是不同的，递增偏移  
"""


def convert(c, key):
    num = ord(c)
    if 33 <= num <= 126:
        # 126-33=93
        num = 33 + (num + key - 33) % 94
    return chr(num)


def encode(s, key):
    o = ""
    for c in s:
        o += convert(c, key)
    return o


def decode(s, key):
    return encode(s, -key)


def decode_all(data, verbose=True):
    p = PrintCollector()
    for key in range(1, 94):
        d = []
        for i, t in enumerate(data):
            k = (key + i) % 94
            r = decode(t, k)
            d.append(r)

        p.print(''.join(d))

    p.print('')
    for key in range(1, 94):
        d = []
        for i, t in enumerate(data):
            k = (key + i) % 94
            r = encode(t, k)
            d.append(r)

        p.print(''.join(d))

    return p.smart_output(verbose=verbose)


def main():
    s = """afZ_r9VYfScOeO_UL^RWUc"""
    decode_all(s)


if __name__ == '__main__':
    main()
