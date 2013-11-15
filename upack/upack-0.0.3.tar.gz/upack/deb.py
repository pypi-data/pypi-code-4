# Copyright (c) 2013, Robert Escriva
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of upack nor the names of its contributors may be used
#       to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import with_statement


import datetime
import glob
import os.path
import shutil
import tarfile
import tempfile

import upack.context
import upack.write


__all__ = ('DebWriter',)


class DebWriter(upack.write.Writer):

    NAME = 'deb'

    def __init__(self):
        super(DebWriter, self).__init__()

    def write(self, ctx, package):
        ctx.push(self.context())
        ctx.push(package)
        basedir = tempfile.mkdtemp(prefix='upack-', dir='.')
        ctx.cleanup(basedir)
        os.mkdir(os.path.join(basedir, 'debian'))
        DIR = lambda x: os.path.join(os.path.join(basedir, 'debian'), x)
        # debian/changelog
        with open(DIR('changelog'), 'w') as fout:
            fout.write(ctx.format('''{source} ({version}-{release}{dist}) unstable; urgency=low

  * Automatically generated using upack

 -- {user_name} <{user_email}>  {date}
'''))
        # debian/compat
        with open(DIR('compat'), 'w') as fout:
            fout.write('8\n')
        # debian/control
        with open(DIR('control'), 'w') as fout:
            fout.write(ctx.format(
'''Source: {source}
Priority: extra
Maintainer: {user_name} <{user_email}>
Build-Depends: debhelper (>= 8.0.0), {build-requires}
Standards-Version: 3.9.3
Section: {section}
Homepage: {homepage}

Package: {name}
Section: {section}
Architecture: any
Depends: ${{shlibs:Depends}}, ${{misc:Depends}}
Description: {summary}
  XXX description
'''))
            for subpackage in package.subpackages:
                ctx.push(subpackage)
                fout.write(ctx.format(
'''
Package: {name}
Section: {section}
Architecture: any
Depends: {requires}
Description: {summary}
  XXX description
'''))
                ctx.pop()
        # debian/copyright
        with open(DIR('copyright'), 'w') as fout:
            fout.write(ctx.format(
'''Format: http://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: {source}
Source: {homepage}

Files: *
Copyright: <years> <put author's name and email here>
           <years> <likewise for another author>
License: {license}

# If you want to use GPL v2 or later for the /debian/* files use
# the following clauses, or change it to suit. Delete these two lines
Files: debian/*
Copyright: {user_name} <{user_email}>
License: same as source
'''))
        # debian/source/format
        os.mkdir(DIR('source'))
        with open(DIR('source/format'), 'w') as fout:
            fout.write('3.0 (quilt)\n')
        # debian/rules
        with open(DIR('rules'), 'w') as fout:
            fout.write(ctx.format(
'''#!/usr/bin/make -f
# -*- makefile -*-
# Sample debian/rules that uses debhelper.
# This file was originally written by Joey Hess and Craig Small.
# As a special exception, when this file is copied by dh-make into a
# dh-make output file, you may use that output file without restriction.
# This special exception was added by Craig Small in version 0.37 of dh-make.

# Uncomment this to turn on verbose mode.
#export DH_VERBOSE=1

%:
	dh $@

override_dh_auto_configure:
	dh_auto_configure -- {configure}

override_dh_auto_install:
	dh_auto_install --destdir=debian/tmp

override_dh_auto_test:

.PHONY: override_dh_auto_configure override_dh_auto_install override_dh_auto_test
'''))
        os.chmod(DIR('rules'), 0755)
        # files
        with open(DIR(package.name + '.install'), 'w') as fout:
            for f in package.files:
                fout.write(ctx.format(f) + '\n')
        for subpackage in package.subpackages:
            ctx.push(subpackage)
            with open(DIR(ctx.format('{name}.install')), 'w') as fout:
                for f in subpackage.files:
                    fout.write(ctx.format(f) + '\n')
            ctx.pop()
        output = ctx.format('{source}_{version}-{release}{dist}.debian.tar.gz')
        output = tarfile.open(output, 'w:gz')
        for x in sorted(glob.glob(basedir + '/debian/*')):
            output.add(x, x[len(basedir) + 1:])
        output.close()
        fout = open(ctx.format('Makefile.deb.{source}'), 'w')
        fout.write(ctx.format(
'''all:
	test '!' -e {source}-{version} || (echo {source}-{version} already exists && exit 2)
	mkdir {source}-{version}
	cp {source}-{version}.tar.gz {source}-{version}/{source}_{version}.orig.tar.gz
	cd {source}-{version} && tar xzvf {source}_{version}.orig.tar.gz
	cd {source}-{version}/{source}-{version} && tar xzvf ../../{source}_{version}-{release}{dist}.debian.tar.gz
	cd {source}-{version}/{source}-{version} && sudo pdebuild
'''))
        ctx.pop()
        ctx.pop()

    def context(self):
        r = upack.context.Raw
        d = {}
        d['date'] = datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S {user_tz}')
        d['dev'] = 'dev'
        d['self'] = r('(= ${binary:Version})')
        d['bindir'] = r('usr/bin')
        d['includedir'] = r('usr/include')
        d['libdir'] = r('usr/lib')
        d['libexecdir'] = r('usr/libexec')
        d['mandir'] = r('usr/share/man')
        return d
