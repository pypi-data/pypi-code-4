#! /usr/bin/env python

import os
import sys
import modulefinder
import subprocess
import textwrap
import pprint
import re

from stat import S_ISREG, ST_CTIME, ST_MODE

__docformat__ = "restructuredtext en"

"""
Width, in characthers, for a CLI program.
"""
WIDTH = 70

def last_made(dirpath='.', suffix=None):
  """
  Returns the most recently created file in `dirpath`.
  The `suffix` parameter is either a single suffix
  (e.g. ``".txt"``) or a sequence of suffices
  (e.g. ``[".txt", ".text"]``).
  """
  # get all entries in the directory w/ stats
  entries = [os.path.join(dirpath, fn) for fn in os.listdir(dirpath)]
  entries = [(os.stat(path), path) for path in entries]

  # leave only regular files, insert creation date
  entries = [(stat[ST_CTIME], path)
             for stat, path in entries if S_ISREG(stat[ST_MODE])]

  if suffix is not None:
    if isinstance(suffix, basestring):
      suffix = (suffix,)
    selected = []
    for sfx in suffix:
      es = [e for e in entries if e[1].endswith(sfx)]
      selected.extend(es)
    entries = selected

  entries.sort(reverse=True)

  if entries:
    result = entries[0][1]
  else:
    result = None

  return result

def wait_exec(cmd, instr=None):
  """
  Waits for `cmd` to execute and returns the output
  from stdout. The `cmd` follows
  the same rules as for python's `popen2.Popen3`.
  If `instr` is provided, this string is passed to
  the standard input of the child process.

  Except for the convenience of passing `instr`, this
  funciton is somewhat redundant with pyhon's `subprocess.call`.
  """
  handle = subprocess.Popen(cmd,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            close_fds=True)

  if instr is None:
    out, err = handle.communicate()
  else:
    out, err = handle.communicate(input=instr)

  if out is None:
    out = ""

  return out


def doyn(msg, cmd=None, exc=os.system, outfile=None):
  """
  Uses the `raw_input` builtin to query the user a
  yes or no question. If `cmd` is provided, then
  the function specified by `exc` (default `os.system`)
  will be called with the argument `cmd`.

  If a file name for `outfile` is provided, then stdout will be
  directed to a file of that name.
  """
  while True:
    yn = raw_input("\n" + msg + " [y or n] ")
    if yn.strip().lower() == "y":
      yn = True
      if cmd is None:
        out = None
      else:
        try:
          out = exc(cmd, outfile=outfile)
        except TypeError:
          out = exc(cmd)
      if out is not None:
        if outfile is None:
          sys.stdout.write(str(out))
          sys.stdout.write("\n")
        else:
          open(outfile, "w").write(out)
      break
    elif yn.strip().lower() == "n":
      yn = False
      break
    print "Didn't understand your response. Answer 'y' or 'n'."
  return yn


def banner(program, version, width=WIDTH):
  """
  Uses the `program` and `version` to print a banner to stdout.
  The banner will be printed at `width` (default 70).
  """
  hline = "=" * width
  sys.stderr.write(hline + "\n")
  p = ("%s v.%s " % (program, version)).center(width) + "\n"
  sys.stderr.write(p)
  sys.stderr.write(hline + "\n")


def usage(parser, msg=None, width=WIDTH):
  """
  Uses the `optparse.OptionParser` to print the usage. If
  `msg` (which can be an `Exception`, `str`, etc.) is supplied
  then it will be printed as an error message, hopefully in a
  way that catches the user's eye. The usage message will
  be formatted at `width` (default 70).
  """
  err = ' ERROR '.center(width, '#')
  errbar = '#' * width
  hline = '=' * width
  if msg is not None:
     print '\n'.join(('', err, str(msg), errbar, ''))
     print hline
  print
  print parser.format_help()
  sys.exit(0)

def get_home_dir():
    """
    Returns the home directory of the account under which
    the python program is executed. The home directory
    is represented in a manner that is comprehensible
    by the host operating system (e.g. ``C:\\something\\``
    for Windows, etc.).
    
    Adapted directly from K. S. Sreeram's approach, message
    393819 on c.l.python (7/18/2006). I treat this code
    as public domain.
    """
    if sys.platform != 'win32' :
        return os.path.expanduser( '~' )
    def valid(path) :
        if path and os.path.isdir(path) :
            return True
        return False
    def env(name) :
        return os.environ.get( name, '' )
    homeDir = env( 'USERPROFILE' )
    if not valid(homeDir) :
        homeDir = env( 'HOME' )
        if not valid(homeDir) :
            homeDir = '%s%s' % (env('HOMEDRIVE'),env('HOMEPATH'))
            if not valid(homeDir) :
                homeDir = env( 'SYSTEMDRIVE' )
                if homeDir and (not homeDir.endswith('\\')) :
                    homeDir += '\\'
                if not valid(homeDir) :
                    homeDir = 'C:\\'
    return homeDir

def get_data_path(env_var, data_dir, package_name):
  """
  Returns the path to the data directory. First
  it looks for the directory specified in the
  `env_var` environment variable and if that directory
  does not exists, finds `data_dir` in one of the
  following places (in this order):

  1. The package directory (i.e. where the ``__init.py__`` is
     for the package named by the `package_name` parameter)
  2. If the package is a file, the directory holding the package file
  3. If frozen, the directory holding the frozen executable
  4. If frozen, the parent directory of the directory
     holding the frozen executable
  5. If frozen, the first element of `sys.path`

  Thus, if the package were at ``/path/to/my_package``,
  (i.e. with ``/path/to/my_package/__init__.py``),
  then a very reasonable place for the data directory would be
  ``/path/to/my_package/package-data/``.

  The anticipated use of this function is within the package
  with which the data files are associated. For this use,
  the package name can be found with the global variable
  `__package__`. E.g.::

     pth = get_data_path('PACKAGEDATA', 'package-data', __package__)

  This code is adapted from `_get_data_path()`
  from matplotlib ``__init__.py``. Some parts of this code
  are subject to the `matplotlib license`_.

  .. _`matplotlib license`:
     http://matplotlib.sourceforge.net/users/license.html
  """

  if env_var in os.environ:
    p = os.environ[env_var]
    if os.path.isdir(p):
      return p
    else:
      tmplt = 'Path in environment variable "%s" is not a directory.'
      msg = tmplt % env_var
      raise RuntimeError(msg)

  finder = modulefinder.ModuleFinder()
  node = finder.find_module(package_name, None)[1]
  if os.path.isdir(node):
    d = node
  else:
    d = os.path.dirname(node)
  p = os.sep.join([d, data_dir])
  if os.path.isdir(p):
    return p

  if getattr(sys, 'frozen', False):
    exe_path = os.path.dirname(sys.executable)
    p = os.path.join(exe_path, data_dir)
    if os.path.isdir(p):
      return p

    # Try again assuming we need to step up one more directory
    p = os.path.join(os.path.split(exe_path)[0], data_dir)
    if os.path.isdir(p):
      return p

    # Try again assuming sys.path[0] is a dir not a exe
    p = os.path.join(sys.path[0], data_dir)
    if os.path.isdir(p):
      return p

  msg = 'Could not find the %s data files.' % package_name
  raise RuntimeError(msg)


def format_config_dict(config, first_space=None):
  """
  The `config` must be a dictionary or other mapping.
  If given, `first_space` will replace the first space of any
  leading space.
  """
  pp = pprint.PrettyPrinter(indent=2)
  f = " " + pp.pformat(config)[1:-1]
  f = f.replace(r"\n'", "'")
  f = re.sub(r"\\n +", " ", f)
  f = textwrap.dedent(f)
  if first_space is not None:
    f = f.replace('\n ', '\n' + first_space)
  return f
