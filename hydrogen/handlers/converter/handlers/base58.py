# -*- coding: utf-8 -*-
# created by restran on 2019/04/25
from __future__ import unicode_literals, absolute_import

"""Base58 encoding
Implementations of Base58 and Base58Check encodings that are compatible
with the bitcoin network.
"""

# 58 character alphabet used
# 比特币地址、Monero 地址
alphabet_bitcoin = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
# Ripple 地址
alphabet_ripple = b'rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz'
# Flickr 的短URL
alphabet_flickr = b'123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'

if bytes == str:  # python2
    iseq, bseq, buffer = (
        lambda s: map(ord, s),
        lambda s: ''.join(map(chr, s)),
        lambda s: s,
    )
else:  # python3
    iseq, bseq, buffer = (
        lambda s: s,
        bytes,
        lambda s: s.buffer,
    )


def scrub_input(v):
    if isinstance(v, str) and not isinstance(v, bytes):
        v = v.encode('ascii')

    return v


def b58encode_int(i, default_one=True, alphabet=alphabet_bitcoin):
    """Encode an integer using Base58"""
    if not i and default_one:
        return alphabet[0:1]
    string = b""
    while i:
        i, idx = divmod(i, 58)
        string = alphabet[idx:idx + 1] + string
    return string


def b58encode(v, alphabet=alphabet_bitcoin):
    """Encode a string using Base58"""
    v = scrub_input(v)

    n_pad = len(v)
    v = v.lstrip(b'\0')
    n_pad -= len(v)

    p, acc = 1, 0
    for c in iseq(reversed(v)):
        acc += p * c
        p = p << 8

    result = b58encode_int(acc, default_one=False, alphabet=alphabet)

    return alphabet[0:1] * n_pad + result


def b58decode_int(v, alphabet=alphabet_bitcoin):
    """Decode a Base58 encoded string as an integer"""
    v = v.rstrip()
    v = scrub_input(v)

    decimal = 0
    for char in v:
        decimal = decimal * 58 + alphabet.index(char)
    return decimal


def b58decode(v, alphabet=alphabet_bitcoin):
    """Decode a Base58 encoded string"""
    v = v.rstrip()
    v = scrub_input(v)

    orig_len = len(v)
    v = v.lstrip(alphabet[0:1])
    new_len = len(v)

    acc = b58decode_int(v, alphabet=alphabet)

    result = []
    while acc > 0:
        acc, mod = divmod(acc, 256)
        result.append(mod)

    return b'\0' * (orig_len - new_len) + bseq(reversed(result))


def b58decode_ripple(v):
    return b58decode(v, alphabet=alphabet_ripple)


def b58encode_ripple(v):
    return b58encode(v, alphabet=alphabet_ripple)


def b58decode_flickr(v):
    return b58decode(v, alphabet=alphabet_flickr)


def b58encode_flickr(v):
    return b58encode(v, alphabet=alphabet_flickr)


def main():
    x = b58encode(b'123456')
    print(x)
    y = b58decode(x)
    print(y)


if __name__ == '__main__':
    main()
