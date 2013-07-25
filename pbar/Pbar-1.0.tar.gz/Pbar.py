#!/usr/bin/env python

import re
import sys
import os
import math
from time import sleep

__author__ = 'Kyle Laplante'
__date__ = '07/24/2013'

__version__ = '1.0'
__email__ = 'kyle.laplante@gmail.com'

class Pbar:

    '''A class to show a progress bar of a certain file.
    It will display progress up to 100%.

    Example:
        from Pbar import Pbar
        myfile = Pbar(pfile="/tmp/somefile", size='25.9kb, timeout=20')
        myfile.show_progress()

    The above example will watch the file '/tmp/somefile' and display
    the progress up to 25.9kb. If the file does not exist within 20
    seconds then it will raise an exception.

    Example (using fork to get the file):
        from Pbar import Pbar
        import os
        url = 'http://www.someurl.com/path/to/somefile'
        child = os.fork()
        if child == 0:
            os.system('wget %s -q -O /tmp/somefile' %url)
        else:
            myfile = Pbar(pfile='/tmp/somefile', size='120mb', timeout=10)
            myfile.show_progress()

    Required args: pfile, size
        + pfile:
              The file to watch.
        + size:
              The expected total size of the file like '100mb'. (Valid sizes = b, kb, mb, gb).

    Optional args: timeout, show_size_progress
        + timeout:
              The timeout (in seconds) Pbar will wait for the file 
              to exist once show_progress() has been called. This 
              is useful if you are waiting for the file to get created.
              The default is 5 seconds.
        + show_size_progress:
              True or False. Default is False. Setting this to true
              will change the output from showing 'File: and Current size:'
              to showing the 'current size of total size'. This way is not
              best.'''

    def __init__(self, *args, **kwargs):

        '''Required args: pfile, size
            + pfile:
                  String (path to file). The file to watch.
            + size:
                  String of number with denomination. (e.g. 100mb).
                  The expected total size of the file. e.g. '2gb'. (Valid sizes = b, kb, mb, gb).

        Optional args: timeout, show_size_progress
            + timeout:
                  Integer. The timeout (in seconds) Pbar will wait for the file 
                  to exist once show_progress() has been called. This 
                  is useful if you are waiting for the file to get created.
                  The default is 5 seconds.
            + show_size_progress:
                  Boolean. Default is False. Setting this to true
                  will change the output from showing 'File: and Current size:'
                  to showing the 'current size of total size'. This way is not
                  best.'''

        self.show_size_progress = kwargs.get('show_size_progress', False)
        self.timeout = kwargs.get('timeout', 5)
        self.pfile = kwargs.get('pfile', None)
        if not self.pfile:
            raise ValueError("Need to enter a pfile using 'pfile='.")
        self.size = kwargs.get('size', None)
        if not self.size:
            raise ValueError("Need to enter a total size using 'size='.")

        d = re.search('[bkmg]', self.size)
        try:
            self.size_type = self.size[d.start():].lower().strip()
        except AttributeError:
            raise TypeError("size must be in the following format: size='100mb' or size='2gb'.")
        try:
            self.size = float(self.size[:d.start()])
        except (AttributeError, TypeError, ValueError):
            raise TypeError("Need to enter size like format '100mb' or '2gb'.")
        self.size_types = {'b': 1, 'kb': 1024, 'mb': 1048576, 'gb': 1073741824}
        if self.size_type not in self.size_types.keys():
            raise ValueError("Need to enter a valid size type in 'size='. e.g. b,mb,kb,gb")

    def current_size(self):

        '''A method to get the current size of a file.
        It will wait the self.timeout amount of seconds
        for the file to exist before raising an exception
        if it does not exist.'''

        counter = 0
        while counter < self.timeout:
            try:
                return os.path.getsize(self.pfile)
            except OSError, e:
                counter += 1
                sleep(1)
        raise OSError(str(e))

    def show_progress(self):
        counter = 0
        csize = 0
        # I need to have this round up on every number because
        # some distros round up even if the number is N.1. If you 
        # expect the file to be 20mb it may actually 19.1mb.
        # Because of this the file may finish downloading but
        # the script will not think the file is done unless
        # we round up all the way. Very frustrating and ugly.
        while math.ceil(csize) < int(self.size):
            pdone = 100 * float(csize)/float(self.size)
            bars = int(pdone)/4
            sys.stdout.write('\r')
            if self.show_size_progress:
                sys.stdout.write('[%-23s] %.2f%% %.2f of %s%s' %
                    ('='*bars,pdone,float(self.current_size())/float(self.size_types[self.size_type]),self.size,self.size_type))
            else:
                sys.stdout.write('[%-23s] %.2f%% File: %s Size: %s' % ('='*bars,pdone,self.pfile,int(csize*self.size_types[self.size_type])))
            sys.stdout.flush()
            csize = float(self.current_size()) / float(self.size_types[self.size_type])
            sleep(.2)
        sys.stdout.write('\nDone downloading %s!\n' %self.pfile)
