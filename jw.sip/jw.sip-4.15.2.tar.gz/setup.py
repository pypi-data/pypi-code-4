#!/usr/bin/env python

from setuptools import setup
from distutils.extension import Extension
from distutils.command.build_ext import build_ext
from distutils import log
import subprocess
import sysconfig
import os

SIP_DIR = 'sip-4.15.2'

with open('MANIFEST.in', 'w') as manifest:
    manifest.write('recursive-include %s *\n' % SIP_DIR)

class GmakeProject(Extension):
    '''
    An extension which is a GNU make based project

    This *must* be a subclass of *distutils.extension.Extension* to make *bdist_egg* happy.
    '''

    def __init__(self, name, **kw):
        '''
        Create new GmakeProject object
        '''
        Extension.__init__(self, name, [])
        self.param = kw
        self.param.setdefault('make', ['make'])

class buildExt(build_ext):
    '''
    Build extension
    '''

    def run(self):
        '''
        Build project(s)
        '''
        for ext in self.distribution.ext_modules:
            script = []
            chdir = ext.param.get('chdir')
            if chdir:
                script.append('cd ' + chdir)
            prep = ext.param.get('prepare')
            if prep:
                if isinstance(prep, (bytes, str)):
                    prep = [prep]
                for c in prep:
                    script.append(c)
            script.append('make')
            shell = ';'.join(script).replace('"', r'\"')
            log.info('Running: %s', shell)
            st = subprocess.check_call('bash -c "%s"' % shell, shell=True)
            if st:
                raise RuntimeError('Make exited with status %d', st)
            results = ext.param.get('results')
            if results:
                self.mkpath(self.build_lib)
                for r in results:
                    if isinstance(r, (tuple, list)):
                        p = os.path.join(*r)
                        r = r[1]
                        if not isinstance(r, (tuple, list)):
                            r = r,
                    else:
                        p = r
                        r = r,
                    if chdir:
                        p = os.path.join(chdir, p)
                    for i in r:
                        self.copy_file(p, os.path.join(self.build_lib, i))

setup(
    name='jw.sip',
    version='4.15.2',
    description='SIP as a dependency for Python packages',
    author='Johnny Wezel',
    author_email='dev-jay@wezel.name',
    download_url='https://pypi.python.org/pypi/jw.sip',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: Freely Distributable',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: C++',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    platforms=[
        'POSIX',
        'Windows'
    ],
    license='GPL',
    long_description=open('README.rst').read(),
    ext_modules=[
        GmakeProject(
            'sip',
            chdir=SIP_DIR,
            prepare='python configure.py -p %s-g++' % sysconfig.get_platform().partition('-')[0],
            results=[('siplib', 'sip%s' % sysconfig.get_config_var('SO'))]
        )
    ],
    scripts =[
        '%s/sipgen/sip%s' % (SIP_DIR, sysconfig.get_config_var('EXE'))
    ],
    cmdclass = {
        'build_ext': buildExt
    }
)
