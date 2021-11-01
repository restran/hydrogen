# -*- coding: utf-8 -*-
# Created by restran on 2017/8/14
from __future__ import unicode_literals, absolute_import
from mountains.utils import PrintCollector

"""
手机9宫格键盘编码
"""

dict_map = {
    '21': 'a', '22': 'b', '23': 'c',
    '31': 'd', '32': 'e', '33': 'f',
    '41': 'g', '42': 'h', '43': 'i',
    '51': 'j', '52': 'k', '53': 'l',
    '61': 'm', '62': 'n', '63': 'o',
    '71': 'p', '72': 'q', '73': 'r', '74': 's',
    '81': 't', '82': 'u', '83': 'v',
    '91': 'w', '92': 'x', '93': 'y', '94': 'z',
    '01': ' '
}


def decode(data, verbose=False):
    p = PrintCollector()
    data = data.replace(' ', '').replace('\t', '').strip()
    # if len(data) % 2 != 0:
    #     p.print('可能不是9宫格手机键盘编码')
    #     return p.smart_output(verbose=verbose)
    tmp_data = list(data)
    result = []
    while len(tmp_data) > 0:
        k = ''.join(tmp_data[:2])
        tmp_data = tmp_data[2:]
        v = dict_map.get(k)
        if v is None:
            v = ''
            # p.print('可能不是9宫格手机键盘编码')
            # return p.smart_output(verbose=verbose)

        result.append(v)

    result = ''.join(result)
    p.print(result)
    return p.smart_output(result, verbose=verbose)


def main():
    data = '335321414374744361715332'
    decode(data)


if __name__ == '__main__':
    main()
