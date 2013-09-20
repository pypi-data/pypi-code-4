__copyright__ = """ Copyright (c) 2009-2012 Torsten Schmits

This file is part of tek-utils. tek-utils is free software;
you can redistribute it and/or modify it under the terms of the GNU General
Public License version 2, as published by the Free Software Foundation.

tek-utils is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc., 59 Temple
Place, Suite 330, Boston, MA  02111-1307  USA

"""

import os
from itertools import filterfalse, chain

from tek.config import ConfigClient

from tek_utils.extract import extract_files
from tek_utils.gain import gain
from mootag.handler import handle
from mootag.store import Album
from mootag.util.path import music_dirs
import tek_utils.process_album.config

def process_album(args):
    conf = ConfigClient('process_album')
    tempdir = conf('music_tempdir')
    albums = chain(filter(os.path.isdir, args),
                   extract_files(filterfalse(os.path.isdir, args), tempdir))
    def dirs():
        for album in map(music_dirs, albums):
            for dir in album:
                os.chmod(dir, 0o755)
                for file in os.listdir(dir):
                    file = os.path.join(dir, file)
                    if os.path.isfile(file):
                        os.chmod(file, 0o644)
                yield dir
    def handled_albums():
        for dir in dirs():
            try:
                handle(dir)
                yield dir
            except Exception as e:
                print('Error handling album %s:' % dir)
                print(e)
    def stored_dirs():
        for path in handled_albums():
            try:
                yield Album(path).store()
            except Exception as e:
                print(e)
    dirs = list(stored_dirs())
    for dir in dirs:
        gain(dir)
