'''
Module debug
'''

import sys

def D(*args):
    '''
    Debug output
    '''
    sys.stderr.write(''.join([str(a) for a in args]) + '\n')

def softAssert(condition, warning):
    '''
    Issue a warning if a condition is not met

    :param bool condition:
    :param string warning:
    :return condition:
    '''
    if not condition:
        D('WARNING: ', warning)
    return condition
