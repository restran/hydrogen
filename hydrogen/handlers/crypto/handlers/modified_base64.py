# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from base64 import b64decode

from mountains import force_bytes, force_text
from mountains.utils import PrintCollector
from .rot13 import decode_rot13
from utils import smart_text
import string

"""
变形Base64
"""


def decode(data, verbose=False):
    if len(data) % 4 != 0:
        data = data + '=' * (4 - len(data) % 4)

    p = PrintCollector()
    p.print('base64:')
    r = b64decode(force_bytes(data))
    p.print(smart_text(r))

    p.print('\nrot13->base64:')
    r = b64decode(force_bytes(decode_rot13(data)))
    p.print(smart_text(r))

    new_data = []
    for t in data:
        if t in string.ascii_lowercase:
            t = t.upper()
        elif t in string.ascii_uppercase:
            t = t.lower()
        new_data.append(t)
    r = ''.join(new_data)
    p.print('\nswap_case->base64:')
    r = b64decode(force_bytes(r))
    p.print(smart_text(r))

    new_data = data[::-1]
    new_data = new_data.lstrip('=')
    if len(new_data) % 4 != 0:
        new_data = new_data + '=' * (4 - len(new_data) % 4)
    r = b64decode(force_bytes(new_data))
    p.print('\nreverse->base64:')
    p.print(smart_text(r))

    return p.smart_output(verbose=verbose)
