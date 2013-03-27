"""This is an automatically generated file created by stsci.distutils.hooks.version_setup_hook.
Do not modify this file by hand.
"""

__all__ = ['__version__', '__vdate__', '__svn_revision__', '__svn_full_info__',
           '__setup_datetime__']

import datetime

__version__ = '0.3.2'
__vdate__ = 'unspecified'
__svn_revision__ = '23957'
__svn_full_info__ = 'Path: stsci.distutils-0.3.2-SjZIz2\nWorking Copy Root Path: /tmp/stsci.distutils-0.3.2-SjZIz2\nURL: https://svn.stsci.edu/svn/ssb/stsci_python/stsci.distutils/tags/0.3.2\nRepository Root: https://svn.stsci.edu/svn/ssb/stsci_python\nRepository UUID: fe389314-cf27-0410-b35b-8c050e845b92\nRevision: 23957\nNode Kind: directory\nSchedule: normal\nLast Changed Author: embray\nLast Changed Rev: 23957\nLast Changed Date: 2013-03-27 13:51:01 -0400 (Wed, 27 Mar 2013)'
__setup_datetime__ = datetime.datetime(2013, 3, 27, 13, 52, 26, 506487)

# what version of stsci.distutils created this version.py
stsci_distutils_version = '0.3.2'


def update_svn_info():
    """Update the SVN info if running out of an SVN working copy."""

    import os
    import string
    import subprocess

    global __svn_revision__
    global __svn_full_info__

    # Wind up the module path until we find the root of the project
    # containing setup.py
    path = os.path.abspath(os.path.dirname(__file__))
    dirname = os.path.dirname(path)
    setup_py = os.path.join(path, 'setup.py')
    while path != dirname and not os.path.exists(setup_py):
        path = os.path.dirname(path)
        dirname = os.path.dirname(path)
        setup_py = os.path.join(path, 'setup.py')

    try:
        pipe = subprocess.Popen(['svnversion', path],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if pipe.wait() == 0:
            stdout = pipe.stdout.read().decode('latin1').strip()
            if stdout and stdout[0] in string.digits:
                __svn_revision__ = stdout
    except OSError:
        pass

    try:
        pipe = subprocess.Popen(['svn', 'info', path],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if pipe.wait() == 0:
            lines = []
            for line in pipe.stdout.readlines():
                line = line.decode('latin1').strip()
                if not line:
                    continue
                lines.append(line)

            if not lines:
                __svn_full_info__ = 'unknown'
            else:
                __svn_full_info__ = '\n'.join(lines)
    except OSError:
        pass


update_svn_info()
del update_svn_info
