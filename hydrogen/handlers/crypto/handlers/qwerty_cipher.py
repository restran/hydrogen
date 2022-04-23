# -*- coding: utf-8 -*-
# Created by restran on 2017/8/14
from __future__ import unicode_literals, absolute_import
from mountains.utils import PrintCollector

"""
PC键盘的 qwerty 替换 abcdefg
"""

raw_map = 'abcdefghijklmnopqrstuvwxyz'

# 标准 qwerty 键盘
dict_map1 = 'qwertyuiopasdfghjklzxcvbnm'
# 从上到下，从左到右
dict_map2 = 'qazwsxedcrfvtgbyhnujmikolp'
# qwerty 逆序
dict_map3 = 'mnbvcxzlkjhgfdsapoiuytrewq'

# CTF不常见的dvorak键盘密码，ypau --> flag
# dvorak键盘
raw_map_dvorak = '{[}]"\'<,>.PpYyFfGgCcRrLl?/+=|\\AaOoEeUuIiDdHhTtNnSs_-:;QqJjKkXxBbMmWwVvZz'
dict_map4 = '_-+=QqWwEeRrTtYyUuIiOoPp{[}]|\\AaSsDdFfGgHhJjKkLl:;"\'ZzXxCcVvBbNnMm<,>.?/'


def decode(data, dict_map):
    data = data.lower()
    result = []
    for t in data:
        if t not in raw_map:
            v = t
        else:
            i = dict_map.index(t)
            v = raw_map[i]
        result.append(v)

    result = ''.join(result)
    return result


def decode_dvorak(data, dict_map):
    data = data.lower()
    result = []
    for t in data:
        if t not in raw_map_dvorak:
            v = t
        else:
            i = dict_map.index(t)
            v = raw_map_dvorak[i]
        result.append(v)

    result = ''.join(result)
    return result


def decode_all(data, verbose=False):
    p = PrintCollector()
    p.print('标准 qwerty 键盘')
    r = decode(data, dict_map1)
    p.print(r)
    p.print('\n从上到下，从左到右')
    r = decode(data, dict_map2)
    p.print(r)
    p.print('\nqwerty 逆序')
    r = decode(data, dict_map3)
    p.print(r)
    # dvorak键盘
    p.print('\ndvorak 键盘')
    r = decode_dvorak(data, dict_map4)
    p.print(r)

    return p.smart_output(verbose=verbose)


def main():
    data = 'kiqlwtfcqgnsoo'
    decode_all(data)


if __name__ == '__main__':
    main()
