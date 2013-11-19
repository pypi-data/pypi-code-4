'''
Created on Nov 1, 2013

@author: Jose Borreguero
'''

import logging
import sys
from pdb import set_trace as tr

class LogLevelFilter(object):
    '''Forces a handle to log only a particular level
    '''
    def __init__(self, level):
        self.__level = level

    def filter(self, logRecord):
        return logRecord.levelno <= self.__level

vlog=logging.getLogger('vizmdend')
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')

# define a Handler which writes WARNING messages or higher to sys.stderr
console_stderr = logging.StreamHandler(sys.stderr)
console_stderr.setLevel(logging.WARNING)
console_stderr.setFormatter(formatter)
vlog.addHandler(console_stderr)

# define a Handler which writes INFO messages to sys.stdout
console_stdout = logging.StreamHandler(sys.stdout)
console_stdout.setLevel(logging.INFO)
console_stdout.addFilter(LogLevelFilter(logging.INFO))
console_stdout.setFormatter(formatter)
vlog.addHandler(console_stdout)
