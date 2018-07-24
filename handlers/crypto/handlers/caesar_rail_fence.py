# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from handlers.crypto.handlers.caesar import decode as caesar_decode
from handlers.crypto.handlers.rail_fence import decode as rail_fence_decode
from mountains.utils import PrintCollector

"""
凯撒困在栅栏里了,需要你的帮助。
sfxjkxtfhwz9xsmijk6j6sthhj

flag格式：NSFOCUS{xxx}，以及之前的格式
"""


def decode(data, verbose=False):
    p = PrintCollector()
    output = rail_fence_decode(data, verbose=False)
    for t in output:
        for key in range(26):
            d = caesar_decode(t, key)
            p.print(d)

    if len(output) == 0:
        p.print('字符串长度为质数，无法自动找到合适的栏数')

    return p.smart_output(verbose=verbose)


def main():
    # data = 'T_ysK9_5rhk__uFMt}3El{nu@E '
    data = 'bcwwylkojh{eznpjbawgoaueee}'
    decode(data)


if __name__ == '__main__':
    main()
