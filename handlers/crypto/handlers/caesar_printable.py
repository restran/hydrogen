# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from mountains.utils import PrintCollector

"""
凯撒密码，实现 33-126 ASCII 可打印的字符循环平移  
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
    for key in range(94):
        r = decode(data, key)
        p.print(r)
    return p.smart_output(verbose=verbose)


def main():
    s = """U8Y]:8KdJHTXRI>XU#?!K_ecJH]kJG*bRH7YJH7YSH]*=93dVZ3^S8*$:8"&:9U]RH;g=8Y!U92'=j*$KH]ZSj&[S#!gU#*dK9\."""
    decode_all(s)


if __name__ == '__main__':
    main()
