__copyright__ = """ Copyright (c) 2009-2013 Torsten Schmits

This file is part of pytek. pytek is free software;
you can redistribute it and/or modify it under the terms of the GNU General
Public License version 2, as published by the Free Software Foundation.

pytek is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc., 59 Temple
Place, Suite 330, Boston, MA  02111-1307  USA

"""

import os
import shutil
import re
import itertools
from unittest import TestCase

from tek import logger
from tek.tools import ymap, Silencer

from tek_utils.extract import ExtractJob

class ExtractTest(TestCase):

    def setUp(self):
        self.basedir = os.path.join(os.path.dirname(__file__), 'data',
                                    'extract')

    def test_types(self):
        os.chdir(self.basedir)
        extensions = ['tar.xz', 'tgz', 'tar.bz2', 'tar.gz', 'tbz2', 'tar.xz',
                      '7z', 'zip', 'rar']
        with Silencer():
            ymap(self.extract_job, extensions)
            ymap(self.extract_job, extensions, use_mime=False)

    def test_multipart(self):
        os.chdir(self.basedir)
        with Silencer():
            job = self.extract_job('part02.rar')
        self.assertTrue(job.archive.path, 'archive.part01.rar')
        self.assertEqual(job.archive._parts, ['archive.part01.rar',
                                              'archive.part02.rar'])

    def extract_job(self, ext, use_mime=True):
        exdir = os.path.join('dest', 'exdir')
        shutil.rmtree(exdir, ignore_errors=True)
        job = ExtractJob('archive.' + ext, dest_dir='dest', use_mime=use_mime,
                         verbose=True)
        job.extract()
        self.assertTrue(os.path.isfile(os.path.join(exdir, 'inside.file')))
        self.assertTrue(os.path.isdir(os.path.join(exdir, 'inside.dir')))
        shutil.rmtree(exdir)
        return job

    def test_list(self):
        os.chdir(self.basedir)
        extensions = ['tar.xz', 'tgz', 'tar.bz2', 'tar.gz', 'tbz2', 'tar.xz',
                      '7z', 'zip', 'rar']
        with Silencer():
            ymap(self.list_job, extensions)

    def list_job(self, ext):
        job = ExtractJob('archive.' + ext, verbose=True, pipe=True)
        job.list()
        output = job.archive.extractor.output
        self.assertTrue(any(map(re.search, itertools.repeat('inside.file'),
                                output)))
        self.assertTrue(any(map(re.search, itertools.repeat('inside.dir'),
                                output)))
