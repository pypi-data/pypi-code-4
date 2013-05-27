'''
'''

import eventlet

class File(file):
    '''
    A greenlet-friendly file
    '''
    def __init__(self, *args, **kwargs):
        super(File, self).__init__(*args, **kwargs)

    def read(self, *args):
        eventlet.sleep(0)
        return super(File, self).read(*args)

    def readline(self, *args):
        eventlet.sleep(0)
        return super(File, self).read(*args)
