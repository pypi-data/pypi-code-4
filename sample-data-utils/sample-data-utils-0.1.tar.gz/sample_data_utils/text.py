# -*- coding: utf-8 -*-
import string
from random import choice, randint


def text(length, choices=string.ascii_letters):
    """ returns a random (fixed length) string

    :param length: string length
    :param choices: string containing all the chars can be used to build the string

    .. seealso::
       :py:func:`rtext`
    """
    return ''.join(choice(choices) for x in range(length))


def rtext(maxlength, minlength=1, choices=string.ascii_letters):
    """ returns a random (variable length) string.

        :param maxlength: maximum string length
        :param minlength: minimum string length
        :param choices: string containing all the chars can be used to build the string

        .. seealso::
           :py:func:`text`
        """
    return ''.join(choice(choices) for x in range(randint(minlength, maxlength)))

