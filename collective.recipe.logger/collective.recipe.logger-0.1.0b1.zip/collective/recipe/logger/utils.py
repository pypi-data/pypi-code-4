""" The module provides utilities """

import time


def id_generator(separator='_'):
    return separator.join(time.ctime().split())
