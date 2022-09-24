# -*- coding: utf-8 -*-
# created by restran on 2022/09/23
import sys

__version__ = '0.1.1'
__all__ = ['b36decode', 'b36encode']

if sys.version_info.major == 2:  # pragma: no cover
    integer_types = (int, long)
else:  # pragma: no cover
    integer_types = (int,)

alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'


def dumps(number):
    """Dumps an integer into a base36 string.

    :param number: the 10-based integer.
    :returns: the base36 string.
    """
    if not isinstance(number, integer_types):
        raise TypeError('number must be an integer')

    if number < 0:
        return '-' + dumps(-number)

    value = ''

    while number != 0:
        number, index = divmod(number, len(alphabet))
        value = alphabet[index] + value

    return value or '0'


def loads(value):
    """Loads a base36 string and parse it into 10-based integer.

    :param value: the base36 string.
    :returns: the parsed integer.
    """
    return int(value, 36)


b36encode = dumps
b36decode = loads
