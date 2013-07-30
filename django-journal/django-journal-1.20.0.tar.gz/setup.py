#!/usr/bin/python
import os

from setuptools import setup, find_packages
from setuptools.command.install_lib import install_lib as _install_lib
from distutils.command.build import build as _build
from distutils.command.sdist import sdist  as _sdist
from distutils.cmd import Command

class compile_translations(Command):
    description = 'compile message catalogs to MO files via django compilemessages'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import os
        import sys
        from django.core.management.commands.compilemessages import \
            compile_messages
        curdir = os.getcwd()
        os.chdir(os.path.realpath('django_journal'))
        compile_messages(stderr=sys.stderr)
        os.chdir(curdir)

class build(_build):
    sub_commands = [('compile_translations', None)] + _build.sub_commands

class sdist(_sdist):
    sub_commands = [('compile_translations', None)] + _sdist.sub_commands

class install_lib(_install_lib):
    def run(self):
        self.run_command('compile_translations')
        _install_lib.run(self)

def get_version():
    import glob
    import re
    import os

    version = None
    for d in glob.glob('*'):
        if not os.path.isdir(d):
            continue
        module_file = os.path.join(d, '__init__.py')
        if not os.path.exists(module_file):
            continue
        for v in re.findall("""__version__ *= *['"](.*)['"]""",
                open(module_file).read()):
            assert version is None
            version = v
        if version:
            break
    assert version is not None
    if os.path.exists('.git'):
        import subprocess
        p = subprocess.Popen(['git','describe','--dirty', '--match=v*'],
                stdout=subprocess.PIPE)
        result = p.communicate()[0]
        assert p.returncode == 0, 'git returned non-zero'
        new_version = result.split()[0][1:]
        major_minor_release = new_version.split('-')[0]
        assert  version == major_minor_release, \
                '__version__ (%s) must match the last git annotated tag (%s)' % (version, major_minor_release)
        version = new_version.replace('-', '.')
    return version

setup(name='django-journal',
        version=get_version(),
        license='AGPLv3',
        description='Keep a structured -- i.e. not just log strings -- journal'
                    ' of events in your applications',
        url='http://dev.entrouvert.org/projects/django-journal/',
        download_url='http://repos.entrouvert.org/django-journal.git/',
        author="Entr'ouvert",
        author_email="info@entrouvert.com",
        packages=find_packages(os.path.dirname(__file__) or '.'),
        include_package_data=True,
        cmdclass={'build': build, 'install_lib': install_lib,
            'compile_translations': compile_translations,
            'sdist': sdist},
        install_requires=[
            'django >= 1.4.2',
            'django-model-utils<1.4',
        ],
        setup_requires=[
            'django >= 1.4.2',
        ],
)
