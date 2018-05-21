#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import string
from copy import deepcopy
from mountains.utils import PrintCollector

alphabet = string.ascii_letters.upper()

"""
培根有两种加密方法，第二种，I/J = abaaa，U/V = baabb 共用一个编码
"""

first_cipher = [
    "aaaaa", "aaaab", "aaaba", "aaabb", "aabaa", "aabab", "aabba", "aabbb", "abaaa", "abaab", "ababa",
    "ababb", "abbaa", "abbab", "abbba", "abbbb", "baaaa", "baaab", "baaba", "baabb", "babaa", "babab",
    "babba", "babbb", "bbaaa", "bbaab"
]

second_cipher = [
    "aaaaa", "aaaab", "aaaba", "aaabb", "aabaa", "aabab", "aabba", "aabbb", "abaaa", "abaaa", "abaab",
    "ababa", "ababb", "abbaa", "abbab", "abbba", "abbbb", "baaaa", "baaab", "baaba", "baabb", "baabb",
    "babaa", "babab", "babba", "babbb"
]


def encode(data, p):
    e_string1 = ""
    e_string2 = ""
    for index in data:
        for i in range(0, 26):
            if index == alphabet[i]:
                e_string1 += first_cipher[i]
                e_string2 += second_cipher[i]
                break
    p.print("first encode method:\n%s" % e_string1)
    p.print("second encode method:\n%s" % e_string2)
    return


def decode_method_1(data, p):
    new_data = list(data)
    result = []
    while len(new_data) > 0:
        t = new_data[:5]
        if len([c for c in t if c in 'abAB']) < 5:
            result.append(t[0])
            new_data = new_data[1:]
            continue
        else:
            new_data = new_data[5:]

        index = None
        t = ''.join(t)
        for i in range(len(first_cipher)):
            if t.lower() == first_cipher[i]:
                index = i
                break
        if index is None:
            print('method_1: 解码%s失败' % t)
        else:
            c = alphabet[index]
            result.append(c)

    p.print("first encode method:")
    p.print(''.join(result))


def decode_method_2(data, p):
    new_data = list(data)
    cipher_dict = second_cipher
    result_list = [[]]
    while len(new_data) > 0:
        t = new_data[:5]
        if len([c for c in t if c in 'abAB']) < 5:
            for x in result_list:
                x.append(t[0])
            new_data = new_data[1:]
            continue
        else:
            new_data = new_data[5:]

        index = None
        t = ''.join(t)
        for i in range(len(cipher_dict)):
            if t.lower() == cipher_dict[i]:
                index = i
                break
        if index is None:
            p.print('method_2: 解码%s失败' % t)
            continue

        # 8 是 i, 19 是 u
        if index in [8, 19]:
            c1 = alphabet[index]
            c2 = alphabet[index + 1]

            tmp_result_list = deepcopy(result_list)
            for x in tmp_result_list:
                x.append(c1)
            for x in result_list:
                x.append(c2)
            result_list.extend(tmp_result_list)
        else:
            c = alphabet[index]
            for x in result_list:
                x.append(c)

    p.print("second encode method:")
    for x in result_list:
        p.print(''.join(x))


def decode(data, verbose=False):
    p = PrintCollector()
    data = ''.join([t for t in data.lower() if t in ('a', 'b')])

    for mode in range(2):
        if mode == 0:
            # e_array = re.findall(".{5}", data)
            new_data = data
        else:
            # 互换 a 和 b
            p.print('-----------------')
            p.print('互换 a 和 b')
            new_data = ''.join(['b' if t == 'a' else 'b' for t in data])
            # e_array = re.findall(".{5}", new_data)

        decode_method_1(new_data, p)
        decode_method_2(new_data, p)
    return p.smart_output(verbose=verbose)


def decode_old(data, verbose=False):
    p = PrintCollector()
    data = ''.join([t for t in data.lower() if t in ('a', 'b')])

    for mode in range(2):
        if mode == 0:
            e_array = re.findall(".{5}", data)
        else:
            # 互换 a 和 b
            p.print('-----------------')
            p.print('互换 a 和 b')
            new_data = ''.join(['b' if t == 'a' else 'b' for t in data])
            e_array = re.findall(".{5}", new_data)

        d_string1 = ""
        d_string2 = ""
        for index in e_array:
            for i in range(0, 26):
                if index == first_cipher[i]:
                    d_string1 += alphabet[i]
                if index == second_cipher[i]:
                    d_string2 += alphabet[i]

        p.print("first method: \n" + d_string1)
        p.print("\nsecond method: \n" + d_string2)
    return p.smart_output(verbose=verbose)
