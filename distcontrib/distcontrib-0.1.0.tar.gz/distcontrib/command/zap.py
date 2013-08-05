#!/usr/bin/env python

from distutils.core import Command


class zap(Command):

    description = 'Remove all unneeded files'

    user_options = [
        ('files=',    'f', "file patterns. default: -f '*~,*.pyc,*.so'"),
        ('dirs=',     'd', "directory patterns. default: -d 'build,dist,*.egg-info'"),
        ('c-files',   'c', "also delete '*.c' files"),
        ('cpp-files', 'p', "also delete '*.cpp' files") ]
    boolean_options = ['c-files', 'cpp-files']
    help_options    = [ ]
    negative_opt    = { }
    sub_commands    = [ ]

    def initialize_options(self):
        self.files = None
        self.dirs  = None
        self.c_files = False
        self.cpp_files = False

    def finalize_options(self):
        if self.files is None:
            self.files = '*~,*.pyc,*.so'
        if self.dirs is None:
            self.dirs  = 'build,dist,*.egg-info'
        if self.c_files:
            self.files = self.files + ',*.c'
        if self.cpp_files:
            self.files = self.files + ',*.cpp'
        # convert to list
        self.dirs  = self.__split(self.dirs)
        self.files = self.__split(self.files)
        #print(self.dirs)
        #print(self.files)

    def run(self):
        from distcontrib import tools

        if self.dry_run:
            print("Don't worry: this is a simulation.")
        # remove files
        for base in self.dirs:
            self.__remove(base=base)
        # remove directories
        self.__remove(names=self.files, kind='f')
        # remove __pycache__
        for cache in tools.findfile(names=['__pycache__'], kind='d', topdown=False):
            self.__remove(base=cache)

    def __remove(self, base='.', names=[], kind=None):
        import os
        from distcontrib import tools
        for fn in tools.findfile(base=base, names=names, kind=kind, topdown=False):
            if os.path.isfile(fn):
                if self.dry_run:
                    print('rm    ' + fn)
                else:
                    os.remove(fn)
            elif os.path.isdir(fn):
                if self.dry_run:
                    print('rmdir ' + fn)
                else:
                    os.rmdir(fn)

    import re
    __spaces = re.compile( ',[ \t]+' )

    def __split(self, s):
        s = self.__spaces.sub(',', s)
        return map((lambda x: x.strip()), s.split(','))
