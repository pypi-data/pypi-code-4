from random import randint
import string
from sample_data_utils.text import text


def digits(length):
    """
        return a random integer

    :param length: number of digits
    """
    return int(text(int(length), choices=string.digits))


def hexnum(length):
    """
        return a random  string represents hexadecimal number of `length` size

    :param length: length (without 0x prefix)
    """
    return text(int(length), choices=string.hexdigits)


def binary(length):
    """
        returns a a random string that represent a binary representation

    :param length: number of bits
    """
    num = randint(1, 999999)
    mask = '0' * length
    return (mask + ''.join([str(num >> i & 1) for i in range(7, -1, -1)]))[-length:]
