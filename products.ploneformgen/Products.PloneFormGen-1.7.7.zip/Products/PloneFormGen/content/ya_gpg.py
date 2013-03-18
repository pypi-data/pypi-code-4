"""
ya_gpg: Yet Another GPG Module
"""
__author__ = 'Steve McMahon <steve@dcn.org>'
__docformat__ = 'plaintext'


# ya_gpg: Yet Another GPG Module ...
#
# I've done a terrible thing, adding yet another gpg module to yet another
# Zope/Plone product. My only excuses are that 1) I didn't want to
# unnecessarily add a dependency to another product; and 2) I needed some
# functionality I didn't find in other products.
#
# IMHO, we need a robust product that provides encryption
# services as a tool.
#
# This module is based on PloneFormMailer's gpg.py, which in turn
# was based on the python-gpg project (since abandoned).
#
# The PloneFormMailer gpg.py module's details are:
# # Author:       Jens Klein <jens.klein@jensquadrat.com>
# # copied:       parts from python-gpg project (unfinished)
# #
# # Copyright:    (c) 2004 by jens quadrat, Klein & Partner KEG, Austria
# # Licence:      GNU General Public Licence (GPL) Version 2 or later
#
#
# Changes by SteveM:
#
#  - add --no-secmem-warning flag
#  - don't fail silently.
#    raise exceptions for failures
#  - don't use --status-fd mode, so errors are easier to detect;
#    module wasn't doing anything with them anyway.
#  - if in windows, look for gpg.exe.
#  - add module global gpg object, mainly to avoid
#    repeated path searches, and make it easy to detect
#    when gpg binary is available.

import os
import subprocess


class GPGError(ValueError):
    " Error from GPG "


class gpg_subprocess:

    # Default path used for searching for the GPG binary, when the
    # PATH environment variable isn't set.
    DEFAULT_PATH = ['/bin', '/usr/bin', '/usr/local/bin']

    def __init__(self, gpg_binary=None):
        """Initialize an object instance.  Options are:

        gpg_binary -- full pathname for GPG binary.  If not supplied,
        the current value of PATH will be searched, falling back to the
        DEFAULT_PATH class variable if PATH isn't available.
        """
        # If needed, look for the gpg binary along the path
        if gpg_binary is None:
            if os.name == 'nt':
                bin_name = 'gpg.exe'
            else:
                bin_name = 'gpg'
            gpg_binary = self._findbinary(bin_name)
        self.gpg_binary = gpg_binary
        if gpg_binary is None:
            raise IOError, "Unable to find gpg binary"

    def _findbinary(self, binname):
        if 'PATH' in os.environ:
            path = os.environ['PATH']
            path = path.split(os.pathsep)
        else:
            path = self.DEFAULT_PATH
        for dir in path:
            fullname = os.path.join(dir, binname)
            if os.path.exists(fullname):
                return fullname
        return None

    def _open_subprocess(self, *args):
        # Internal method: open a pipe to a GPG subprocess and return
        # the file objects for communicating with it.
        # cmd = self.gpg_binary + ' --yes --status-fd 2 ' + string.join(args)
        cmd = str(self.gpg_binary + ' --batch --yes --trust-model always --no-secmem-warning ' + " ".join(args))
        PIPE = subprocess.PIPE
        p = subprocess.Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        child_stdout, child_stdin, child_stderr = (p.stdout, p.stdin, p.stderr)
        return child_stdout, child_stdin, child_stderr

    def encrypt(self, data, recipient_key_id):
        "Encrypt the message contained in the string 'data'"

        PIPE = subprocess.PIPE
        cmd = '%s --batch --yes --trust-model always --no-secmem-warning --encrypt -a -r %s' % (self.gpg_binary, recipient_key_id)
        p = subprocess.Popen(str(cmd), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)

        # feed data
        p.stdin.write(data)
        p.stdin.close()

        if p.returncode:
            raise GPGError, p.stderr.read().replace('\n', '; ')

        # get response
        datagpg = p.stdout.read()

        return datagpg


try:
    gpg = gpg_subprocess()
except IOError:
    gpg = None


if __name__ == '__main__':
    if gpg:
        data = gpg.encrypt('BLABLA', 'steve@...')
        print data
    else:
        print "gpg not available"
