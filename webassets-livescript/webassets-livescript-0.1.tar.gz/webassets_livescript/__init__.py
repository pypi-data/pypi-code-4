import os, subprocess

from webassets.filter import Filter
from webassets.exceptions import FilterError, ImminentDeprecationWarning


__all__ = ('LiveScript',)


class LiveScript(Filter):

    name = 'livescript'
    max_debug_level = None
    options = {
        'ls_bin': ('binary', 'LS_BIN'),
        'no_bare': 'LS_NO_BARE',
    }

    def output(self, _in, out, **kw):
        binary = self.ls_bin or 'livescript'

        args = "-csp" + ("" if self.no_bare else 'b')
        proc = subprocess.Popen([binary, args],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate(_in.read().encode('utf-8'))
        if proc.returncode != 0:
            raise FilterError(('livescript: subprocess had error: stderr=%s, '+
                               'stdout=%s, returncode=%s') % (
                stderr, stdout, proc.returncode))
        elif stderr:
            print("livescript filter has warnings:", stderr)
        out.write(stdout.decode('utf-8'))
    
