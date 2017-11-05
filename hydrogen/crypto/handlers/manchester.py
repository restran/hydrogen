# -*- coding: utf-8 -*-
# Created by restran on 2017/11/4
from __future__ import unicode_literals, absolute_import


def decode(data, mode=0, verbose=False):
    """
    mode 用于控制跳变代表0还是1
    :param data:
    :param mode:
    :param verbose:
    :return:
    """
    i = 1
    n = len(data)
    decoded = ''

    while i < n:
        a = data[i - 1]
        b = data[i]
        i += 2
        if a == "0" and b == "1":
            decoded += '1' if mode else "0"
        elif a == "1" and b == "0":
            decoded += '0' if mode else "1"
        else:
            decoded += "E"

    return decoded


def main():
    s = '1010101010101010101010101010101010010101011010010101101010101010101010101010101001011010101010010101011010101010010101010101011010101010101010100101010101010110101010101010101010101010101010010101'
    decode(s)


if __name__ == '__main__':
    main()
