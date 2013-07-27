#!/usr/bin/env python
# -*- coding: latin1 -*- vim: ts=8 sts=4 sw=4 si et tw=79
"""\
Call the "best" Python 2 interpreter on the system,
to be precise: the highest version below Python 3.

This tool is tested on Windows only, since it is needed there most dearly:
When installing Python there, 'python.exe' is usually not in the PATH!
"Shebang" magical comments are not used there; instead, filename extensions are
ASSOCiated with file types, and file types with programs.

py2.py doesn't query the registry; it looks for directories where Python would
be typically installed (see thebops.likeix.PythonVDirs).

Linux systems look different: 'python' (typically /usr/bin/python) is a
symbolical link to pythonX.Y.  Thus, a search on Linux could check the location
of those link targets for python*.* entries; this is not yet implemented.

To put it short:  On Windows systems (or any system which provides the
Windows-style environment variables SystemDrive etc.), this script should call
always the same Python interpreter, regardless of which one it was called
itself;  otherwise it will probably simply use the first (or only) 'python' in
the PATH.
"""

__author__ = "Tobias Herp <tobias.herp@gmx.net>"
VERSION = (0,
           2,   # fallback to calling interpreter
           'rev-%s' % '$Rev: 991 $'[6:-2],
           )
__version__ = '.'.join(map(str, VERSION))

from sys import argv, executable, version_info, stderr
from subprocess import Popen
from thebops.likeix import find_python, get_best
from thebops.anyos import ProgramNotFound, \
        VersionsUnknown, VersionConstrained
from thebops.errors import info, warn, fatal

try: _
except NameError:
    def _(s): return s

VTUPLE = (3, 0)
def main():
    try:
        PYTHON = get_best(find_python,
                          version_below=VTUPLE)
    except VersionsUnknown, e:
        warn(e)
    except VersionConstrained, e:
        warn(e)
    except ProgramNotFound, e:
        warn(e)
    except Exception, e:
        fatal(e)
    if PYTHON is None:
        warn(_('The current Python interpreter was not found '
               'by thebops.anyos.find_python (%(executable)s)'
               ) % globals())
        myversion = version_info[:len(VTUPLE)]
        myversion_string = '.'.join(myversion)
        constrained_string = '.'.join(VTUPLE)
        if myversion < VTUPLE:
            PYTHON = executable
            info(_('Falling back to calling Python %(myversion_string)s'
                   ) % locals(),
                 to=stderr)
        else:
            fatal(_('Calling Python %(myversion_string)s '
                    'is not below %(constrained_string)s'
                    ) % locals())
    rc = Popen([PYTHON]+argv[1:]).wait()
    raise SystemExit(rc)

if __name__ == '__main__':
    main()
