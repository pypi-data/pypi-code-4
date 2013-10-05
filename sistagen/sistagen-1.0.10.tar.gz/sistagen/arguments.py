# -*- coding: utf-8 -*-

import logging
import sys
from getopt import getopt

from help import print_help



def parse_arguments():
    '''
    Parses command line arguments.
    Returns (OPTIONS, FILES)
    '''

    OPTIONS = {
        'conf-dir': ['.'],
        'out-dir': '.',
        'preserve': False,
        'cmd-line': False
        }


    opts, args = getopt(sys.argv[1:], 
           'hvdqC:O:p',
           [
               'help', 'verbose', 'debug', 'quiet',
               'conf-dir=', 
               'out-dir=',
               'preserve',
               'cmd-line',
           ])
           
    for opt, val in opts:
        if opt in ('-h', '--help'):
            print_help()
            sys.exit(0)
        elif opt in ('-v', '--verbose'):
            logging.getLogger().setLevel(logging.INFO)
        elif opt in ('-d', '--debug'):
            logging.getLogger().setLevel(logging.DEBUG)
        elif opt in ('-q', '--quiet'):
            logging.getLogger().setLevel(logging.CRITICAL)
        elif opt in ('-C', '--conf-dir'):
            OPTIONS['conf-dir'].append(val)
        elif opt in ('-O', '--out-dir'):
            OPTIONS['out-dir'] = val
        elif opt in ('-p', '--preserve'):
            OPTIONS['preserve'] = True
        elif opt in ('--cmd-line'):
            OPTIONS['cmd-line'] = True


    FILES = args   
    
    return OPTIONS, FILES