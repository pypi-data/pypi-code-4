#!/usr/bin/env python

''' A python library to incrementally rotate files'''

import os
import glob

__author__ = 'Kyle Laplante'
__copyright__ = 'Copyright 2013, Kyle Laplante'
__date__ = '07-07-2013'

__license__ = 'GPL'
__version__ = '1.1'
__email__ = 'kyle.laplante@gmail.com'


class LogRotateException(Exception):
    pass


class LogRotate:

    """This library is a simple logrotater (or file rotater).
Simply pass in the path to the main logfile and this
library will rotate all the logs by an increment of 1."""

    def __init__(self, *args, **kwargs):

        '''Required kwargs: prefix="some path"'''

        self.verbose = kwargs.get('verbose', False)
        for k, v in kwargs.items():
            setattr(self, k, v)
        if not os.path.isfile(self.prefix):
            raise LogRotateException("Must use a valid prefix filename")

    def rotate(self, *args, **kwargs):
        self.files = glob.glob(self.prefix + "*")
        if not len(self.files) > 0:
            raise LogRotateException(
                "No files with the prefix %s found" % self.prefix)
        self.nums = []
        for file in self.files:
            try:
                self.nums.append(int(file.split(self.prefix + '.')[-1]))
            except ValueError:
                pass
        self.nums.sort()
        self.nums.reverse()
        for num in self.nums:
            new_num = num + 1
            if self.verbose:
                print "moving %s.%d to %s.%d" % (self.prefix, num, self.prefix, new_num)
            os.rename("%s.%d" % (self.prefix, num), "%s.%d" %
                      (self.prefix, new_num))
        if self.verbose:
            print "moving %s to %s.1" % (self.prefix, self.prefix)
        os.rename(self.prefix, self.prefix + '.1')
        self.touch(self.prefix)

    def touch(self, path):

        '''a simple method to touch a file'''

        if self.verbose:
            print "Creating file: %s" % path
        with open(path, 'a'):
            os.utime(path, None)

if __name__ == '__main__':

    from optparse import OptionParser
    import sys

    usage = '''%prog [options] <file prefix>

File prefix is the path to the main logfile.'''

    parser = OptionParser(usage=usage)
    parser.add_option(
        '-p', '--prefix', dest='prefix', default=None, help='Filename prefix.')
    parser.add_option('-v', '--verbose', dest='verbose',
                      action='store_true', default=False, help='Enable verbose output')
    (opts, args) = parser.parse_args()

    if opts.prefix is None:
        print "Please enter a filename prefix"
        sys.exit(1)

    try:
        rotater = LogRotate(prefix=opts.prefix, verbose=opts.verbose)
    except LogRotateException, e:
        print e
        sys.exit(1)
    try:
        rotater.rotate()
    except LogRotateException, e:
        print e
        sys.exit(1)
