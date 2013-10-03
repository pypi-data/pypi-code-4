#####################################################################
# zopyx.authoring
# (C) 2010, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

import os

def checkCommand(cmd):
    """ Check if 'cmd' exists within $PATH """

    path = os.environ.get('PATH')
    if path is None:
        raise ValueError('$PATH not set')

    for dir in path.split(':'):
        if os.path.exists(os.path.join(dir, cmd)):
            return True
    return False

