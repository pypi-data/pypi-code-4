# -*- coding: utf-8 -*-
"""
Misc utility functions
"""


def variable_is_int(in_string):
    """
    Test if a variable can be cast as an integer

    :param in_string: Inbound value
    :type in_string: str
    :return: Boolean reflecting that it can or cant be cast as an integer
    :rtype: bool
    """
    try:
        int(in_string)
        return True
    except ValueError:
        return False