# -*- coding: utf-8 -*-
# created by restran on 2022/09/23
"""Encode and decode base32 data using arbitrary alphabets"""

import base64
import string

# Define known alphabets for convenience
RFC_3548 = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
RFC_4648 = RFC_3548
RFC_2938 = b"0123456789ABCDEFGHIJKLMNOPQRSTVW"
CROCKFORD = b"0123456789ABCDEFGHJKMNPQRSTVWXYZ"
CROCKFORD_MODIFIED = b"0123456789abcdefghjkmnpqrtuvwxyz"
ZBASE32 = b"ybndrfg8ejkmcpqxot1uwisza345h769"
NIGHTMARE = b"dDO0o1IiLl6bB8UuVvWwNnMmZz2S5s7T"


def validate_alphabet(alphabet):
    """Verify that a base32 alphabet is valid

    Args:
        alphabet (bytes): Ordered, case-sensitive encoding/decoding alphabet

    Raises:
        ValueError: if the alphabet is not valid
    """
    if len(set([i for i in alphabet])) != 32:
        raise ValueError("Invalid base32 alphabet")


def validate_encoded_data(data, alphabet):
    """Verify that an encoded input is valid for a given alphabet

    Args:
        data (bytes): base32 encoded string
        alphabet (bytes): Ordered, case-sensitive encoding alphabet

    Raises:
        TypeError: if the string has characters outside the alphabet
    """
    validate_alphabet(alphabet)
    data_set = set([i for i in data])
    alphabet_set = set([i for i in alphabet])

    if not data_set.issubset(alphabet_set):
        raise TypeError("Non-base32 digit found")


def encode(data, alphabet=None):
    """Encode a string into base32 using a designated alphabet

    Args:
        data (bytes): Data to encode into base32
        alphabet (bytes): Ordered, case-sensitive encoding alphabet
            Default alphabet is RFC3548

    Returns:
        bytes: base-32 encoded bytes
    """
    validate_alphabet(alphabet or RFC_3548)

    encoded = base64.b32encode(data)
    encoded = encoded.rstrip(b'=')

    if alphabet is not None:
        try:
            # Python 2
            translator = string.maketrans(RFC_3548, alphabet)
        except AttributeError:
            # Python 3
            translator = bytes.maketrans(RFC_3548, alphabet)
        encoded = encoded.translate(translator)

    return encoded


def decode(data, alphabet=None):
    """Decode a base32 string using a designated alphabet

    Args:
        data (bytes): Bytes to decode from base32
        alphabet (bytes): Ordered, case-sensitive encoding alphabet
            Default alphabet is RFC3548

    Returns:
        bytes: Decoded bytes
    """
    validate_alphabet(alphabet or RFC_3548)
    validate_encoded_data(data, alphabet or RFC_3548)

    encoded = data
    if alphabet is not None:
        try:
            # Python 2
            translator = string.maketrans(alphabet, RFC_3548)
        except AttributeError:
            # Python 3
            translator = bytes.maketrans(alphabet, RFC_3548)
        encoded = data.translate(translator)

    # base64 module / RFC3548 requires padding for decoding
    encoded += b'=' * ((8 - len(data) % 8) % 8)

    return base64.b32decode(encoded)


any_b32encode = encode
any_b32decode = decode

if __name__ == '__main__':
    x = any_b32encode('123'.encode())
    print(x)
    x = b'IFQWCYI'
    x = any_b32decode(x)
    print(x)
