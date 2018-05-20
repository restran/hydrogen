#!/usr/bin/python
# -*- coding: utf-8 -*-
import string

from mountains.util import PrintCollector

from handlers.crypto.handlers.bacon_cipher import decode_method_1, decode_method_2


def decode(data, verbose=False):
    p = PrintCollector()
    # raw_data = "DEath IS JUST A PaRT oF lIFE, sOMeTHInG wE'RE aLL dESTInED TO dO."
    raw_data = data
    for mode in (0, 1):
        if mode == 0:
            p.print('\n小写为a，大写为b\n')
        else:
            p.print('\n小写为b，大写为a\n')

        new_data = recovery_transformed_bacon_data(p, raw_data, mode)

        # data = 'baabaaabbbabaaabbaaaaaaaaabbabaaaabaaaaa/abaaabaaba/aaabaabbbaabbbaababb'
        # 这种就直接解码
        # data = 'abbab_babbb_baaaa_aaabb'
        decode_method_1(new_data, p)
        decode_method_2(new_data, p)

    return p.smart_output(verbose=verbose)


def recovery_transformed_bacon_data(p, data, mode=0):
    """
    woUld you prEfeR SausaGes or bacoN  wiTH YouR EgG
    这里发现有大写有小写，非常诡异，故猜测大小写各代表两种状态，我们用a,b表示；小写是a,大写是b
    mode: 0 表示 a 为小写，1表示b为小写
    :return:
    """
    if mode == 0:
        p.print('-------a为小写--------')
    else:
        p.print('-------b为小写--------')

    p.print('原始数据: %s' % data)

    new_data = []
    # data='woUld you prEfeR SausaGes or bacoN wiTH YouR EgG'
    data = [t for t in data if t in string.ascii_letters]
    for x, t in enumerate(data):
        if t.isupper():
            if mode == 0:
                new_data.append('b')
            else:
                new_data.append('a')
        else:
            if mode == 0:
                new_data.append('a')
            else:
                new_data.append('b')

    new_data = ''.join(new_data)
    p.print('转换后的数据: %s' % new_data)

    return new_data
