#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import string
from copy import deepcopy
from mountains.util import PrintCollector

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


def encode(data):
    e_string1 = ""
    e_string2 = ""
    for index in data:
        for i in range(0, 26):
            if index == alphabet[i]:
                e_string1 += first_cipher[i]
                e_string2 += second_cipher[i]
                break
    print("first encode method:\n%s" % e_string1)
    print("second encode method:\n%s" % e_string2)
    return


def decode_method_1(data):
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

    print("first encode method:")
    print(''.join(result))


def decode_method_2(data):
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
            print('method_2: 解码%s失败' % t)
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

    print("second encode method:")
    for x in result_list:
        print(''.join(x))


def decode(data, verbose=False):
    p = PrintCollector()
    e_array = re.findall(".{5}", data)
    print(e_array)
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


def recovery_transformed_bacon_data(data):
    """
    woUld you prEfeR SausaGes or bacoN  wiTH YouR EgG
    这里发现有大写有小写，非常诡异，故猜测大小写各代表两种状态，我们用a,b表示；小写是a,大写是b
    :return:
    """
    print('原始数据')
    print(data)
    new_data = []
    # data='woUld you prEfeR SausaGes or bacoN wiTH YouR EgG'
    data = [t for t in data if t in string.ascii_letters]
    for x, t in enumerate(data):
        if t.isupper():
            new_data.append('b')
        else:
            new_data.append('a')

    new_data = ''.join(new_data)
    print('转换后的数据')
    print(new_data)
    return new_data


def main():
    """
    如果遇到i,j,u,v等字符，第二种方法，会有多个输出结果
    :return:
    """
    # data = 'abbabbabbbbaaaaaaabb'
    # encode(data)

    # 遇到这种类型的数据，是用大小写表示a和b，需要转换
    data = "bacoN is one of aMerICa'S sWEethEartS. it's A dARlinG, SuCCulEnt fOoD tHAt PaIRs FlawLE"
    data = recovery_transformed_bacon_data(data)

    # data = 'baabaaabbbabaaabbaaaaaaaaabbabaaaabaaaaa/abaaabaaba/aaabaabbbaabbbaababb'
    # 这种就直接解码
    # data = 'abbab_babbb_baaaa_aaabb'
    decode(data)


if __name__ == '__main__':
    main()
