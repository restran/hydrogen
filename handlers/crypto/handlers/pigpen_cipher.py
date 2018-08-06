# -*- coding: utf-8 -*-
# Created by restran on 2016/12/4
from __future__ import unicode_literals, absolute_import

from mountains.utils import PrintCollector

"""
猪圈密码
"""


def pigpen_cipher(text):
    def do_replace(c):
        a = "abcdefghistuv"
        b = "jklmnopqrwxyz"
        if c.isalpha():
            if c in a:
                n = a.find(c)
                pig = b[n]
            else:
                n = b.find(c)
                pig = a[n]
            return pig
        else:
            return letter

    res = ''
    for letter in text:
        res += do_replace(letter)
    return res


def decode(data, verbose=False):
    p = PrintCollector()
    d = pigpen_cipher(data)
    p.print(d)

    return p.smart_output(verbose=verbose)


if __name__ == '__main__':
    input_data = 'gjcq{cjuoykhdrnqbkhkh}'
    decode(input_data)
