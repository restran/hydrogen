# -*- coding: utf-8 -*-
# created by restran on 2019/09/06
from mountains.utils import PrintCollector
import string

"""
每个字符进行异或，用爆破的方式
"""


def is_printable(s):
    for c in s:
        if c not in string.printable:
            return False
    else:
        return True


def decode_xor(data):
    buff = []
    for i in range(0, 256):
        x = [chr(ord(c) ^ i) for c in data]
        s = ''.join(x)
        if is_printable(s):
            buff.append('0x{:02x}: {}'.format(i, s))

    return '\n'.join(buff)


def decode(data, verbose=False):
    p = PrintCollector()
    d = decode_xor(data)
    p.print(d)

    return p.smart_output(verbose=verbose)


if __name__ == '__main__':
    input_data = "}wz|`Rzvxtvru|f"
    decode(input_data)
