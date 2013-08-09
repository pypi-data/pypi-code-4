#! /usr/bin/env python

# lsprofcalltree.py: lsprof output which is readable by kcachegrind
# David Allouche
# Jp Calderone & Itamar Shtull-Trauring
# Johan Dahlin

import optparse
import os
import os.path
import sys

try:
    import cProfile
except ImportError:
    raise SystemExit("This script requires cProfile from Python 2.5")

def label(code):
    if isinstance(code, str):
        return ('~', 0, code)    # built-in functions ('~' sorts at the end)
    else:
        return '%s %s:%d' % (code.co_name,
                             code.co_filename,
                             code.co_firstlineno)

class KCacheGrind(object):
    def __init__(self, profiler):
        self.data = profiler.getstats()
        self.out_file = None

    def output(self, out_file):
        self.out_file = out_file
        print >> out_file, 'events: Ticks'
        self._print_summary()
        for entry in self.data:
            self._entry(entry)

    def _print_summary(self):
        max_cost = 0
        for entry in self.data:
            totaltime = int(entry.totaltime * 1000)
            max_cost = max(max_cost, totaltime)
        print >> self.out_file, 'summary: %d' % (max_cost,)

    def _entry(self, entry):
        out_file = self.out_file

        code = entry.code
        #print >> out_file, 'ob=%s' % (code.co_filename,)
        if isinstance(code, str):
            print >> out_file, 'fi=~'
        else:
            print >> out_file, 'fi=%s' % (code.co_filename,)
        print >> out_file, 'fn=%s' % (label(code),)

        inlinetime = int(entry.inlinetime * 1000)
        if isinstance(code, str):
            print >> out_file, '0 ', inlinetime
        else:
            print >> out_file, '%d %d' % (code.co_firstlineno, inlinetime)

        # recursive calls are counted in entry.calls
        if entry.calls:
            calls = entry.calls
        else:
            calls = []

        if isinstance(code, str):
            lineno = 0
        else:
            lineno = code.co_firstlineno

        for subentry in calls:
            self._subentry(lineno, subentry)
        print >> out_file

    def _subentry(self, lineno, subentry):
        out_file = self.out_file
        code = subentry.code
        #print >> out_file, 'cob=%s' % (code.co_filename,)
        print >> out_file, 'cfn=%s' % (label(code),)
        if isinstance(code, str):
            print >> out_file, 'cfi=~'
            print >> out_file, 'calls=%d 0' % (subentry.callcount,)
        else:
            print >> out_file, 'cfi=%s' % (code.co_filename,)
            print >> out_file, 'calls=%d %d' % (
                subentry.callcount, code.co_firstlineno)

        totaltime = int(subentry.totaltime * 1000)
        print >> out_file, '%d %d' % (lineno, totaltime)

def search_path(name, path=None, exts=('',)):
  """Search PATH for a binary.

  # from http://code.activestate.com/recipes/52224-find-a-file-given-a-search-path/

  Args:
    name: the filename to search for
    path: the optional path string (default: os.environ['PATH')
    exts: optional list/tuple of extensions to try (default: ('',))

  Returns:
    The abspath to the binary or None if not found.
  """
  path = path or os.environ['PATH']
  for dir in path.split(os.pathsep):
    for ext in exts:
      binpath = os.path.join(dir, name) + ext
      if os.path.exists(binpath):
        return os.path.abspath(binpath)
  return None

# Shamelessly stolen from ipython
def init_virtualenv():
    """Add a virtualenv to sys.path so the user can import modules from it.
    This isn't perfect: it doesn't use the Python interpreter with which the
    virtualenv was built, and it ignores the --no-site-packages option. A
    warning will appear suggesting the user installs IPython in the
    virtualenv, but for many cases, it probably works well enough.
    
    Adapted from code snippets online.
    
    http://blog.ufsoft.org/2009/1/29/ipython-and-virtualenv
    """
    if 'VIRTUAL_ENV' not in os.environ:
        # Not in a virtualenv
        return
    
    if sys.executable.startswith(os.environ['VIRTUAL_ENV']):
        # Running properly in the virtualenv, don't need to do anything
        return
    
    print ("Attempting to work in a virtualenv. If you encounter problems, please "
         "install lpct inside the virtualenv.")
    if sys.platform == "win32":
        virtual_env = os.path.join(os.environ['VIRTUAL_ENV'], 'Lib', 'site-packages') 
    else:
        virtual_env = os.path.join(os.environ['VIRTUAL_ENV'], 'lib',
                   'python%d.%d' % sys.version_info[:2], 'site-packages')
    
    import site
    sys.path.insert(0, virtual_env)
    site.addsitedir(virtual_env)


def main():

    init_virtualenv()

    usage = "%s [-o output_file_path] scriptfile [arg] ..."
    parser = optparse.OptionParser(usage=usage % sys.argv[0])
    parser.allow_interspersed_args = False
    parser.add_option('-o', '--outfile', dest="outfile",
                      help="Save stats to <outfile>", default=None)

    if not sys.argv[1:]:
        parser.print_usage()
        sys.exit(2)

    options, args = parser.parse_args()

    if not options.outfile:
        options.outfile = 'lpct-%s.log' % os.path.basename(args[0])

    cmd = args[0]
    if not os.path.exists(cmd):
        cmd = search_path(cmd)

    prof = cProfile.Profile()
    try:
        try:
            prof = prof.run('execfile({0!r})'.format(cmd))
        except SystemExit:
            pass
    finally:
        kg = KCacheGrind(prof)
        kg.output(file(options.outfile, 'w'))
        print "lpct: now run:"
        print "kcachegrind {0}".format(options.outfile)
