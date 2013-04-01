#!/usr/bin/env python
# -*- coding: latin1 -*- vim: ts=8 sts=4 sw=4 si et tw=79
"""\
thebops.likeix.py: find POSIX-conforming tools, even on Windows(TM) systems

This module serves two purposes:
- when calling a program without using the shell, the PATH is not searched.
  The functions in this module yield absolute paths.

  The find_progs function (anyos module) tries to ferret out all occurrences
  on the system, using a smart strategy:
  0. (for configuration files; typically not used for executables)
     searches a directory and all of its *parents* (not: children!)
  1. searches a specified set of directories.
     Some tools install on Win* in some directory somewhere below
     %ProgramFiles% which are not available in the PATH.
     find_progs optionally takes a sequence of directory specs which
     may contain environment variable names in Python's dict comprehension
     syntax; if the variable is unknown, the entry is ignored.
     (Of course, this is way faster than searching an entire harddisk.)
  2. Searches the PATH.
     When doing this, some directories can be excluded (the xroots argument)
     which contain very likely programs which don't behave like the desired
     POSIX tool at all, e.g. %(SystemRoot)%.

- for some often needed programs, there are certain useful strategies,
  and some well- (or not-so-well-) known environment variables.

  This module contains some special functions which salt the anyos.find_progs
  function with appropriate defaults.
  When seeking a certain program in various scripts, just update (or add!) the
  respective function in this module, rather than updating every single script.

Of course, you are welcome to tell the author about your additions :-)

As long as the strategies of the functions in this module are sufficient to
you, all you need to do is something like

    from thebops.likeix import ToolsHub
    hub = ToolsHub()
    print hub['sed']

... which will give you the complete path to the 'sed' program which was found
for you on your system, or None.

"""

__author__ = "Tobias Herp <tobias.herp@gmx.net>"
VERSION = (0,
           3,   # ToolsHub (no demo so far)
           3,   # UnxUtils
           'rev-%s' % '$Rev: 938 $'[6:-2],
           )
__version__ = '.'.join(map(str, VERSION))
__all__ = ['ToolsHub',      # smart wrapper for find_progs
           'find_progs',    # from anyos.py
           # wrappers for find_progs:
           'find_diff',
           'find_find',
           'find_grep',
           'find_ln',
           'find_python',
           'find_sed',
           'find_sort',
           'find_svn',
           'find_tsvn',
           'find_uniq',
           'find_vim',
           'find_gvim',
           # ... for the PuTTY suite:
           'find_putty',
           'find_pscp',
           'find_psftp',
           'find_plink',
           'find_pageant',
           # ... or any generic POSIX tool:
           'find_PosixTool',
           # wrap them all and take the 1st/best:
           'get_1st',
           'get_best',
           # indirs generation:
           'ProgramDirs',
           'PosixToolsDirs',
           'CygwinDirs',
           # ... there are more, but you won't need to use them directory
           # data:
           'WINDOWS_ROOTS',
           # exceptions, from anyos.py:
           'ProgramNotFound',
           'VersionsUnknown',
           'VersionConstrained',
           ]

from os import environ
from os.path import pathsep, sep, join, abspath
from thebops.anyos import find_progs, ProgramNotFound, vdir_digits, \
        VersionsUnknown, VersionConstrained

try:    # i18n-Dummy
    _
except NameError:
    _ = lambda s: s

def get_1st(f, **kwargs):
    """
    call the given find_... function and return the 1st hit

    f -- the name of the program as a non-unicode string (the wrapper function
         being find_<f>), or a generator function.

    The function will yield a KeyError if a string is given, and the
    respective find_<f> function doesn't exist in this module.

    Additional keyword arguments can be specified and are passed on to the
    function
    """
    if isinstance(f, str):
        f = globals()['find_%s' % f]
    for item in f(**kwargs):
        return item
    if 'progname' in kwargs:
        raise ProgramNotFound('%(progname)s not found' % kwargs)
    elif f.__name__.startswith('find_'):
        progname = f.__name__[5:] or '<unknown program>'
        raise ProgramNotFound('%(progname)s not found' % locals())
    else:
        raise ProgramNotFound('%r not successful' % f)

def get_best(f,
             version_func=vdir_digits,
             version_below=None,
             **kwargs):
    """
    call the given find_... function and return the best hit

    f -- the name of the program as a non-unicode string (the wrapper function
         being find_<f>), or a generator function.

    version_func -- a function which extracts version info from each hit.
                    The default, <vdir_digits>, simply inspects the directory
                    for version information and returns e.g. (7, 2) for
                    .../vim72 directories, which is fine e.g. for vim and
                    python installations on Windows systems.

    version_below -- a version to stay below; e.g. to avoid python 3
                     interpreters, specify (3, 0)

    The function will yield a KeyError if a string is given for <f>, and the
    respective find_<f> function doesn't exist in this module.
    If seeked, but w/o success, a ProgramNotFound exception or one of its
    descendants is raised.

    Additional keyword arguments can be specified and are passed on to the
    function
    """
    if isinstance(f, str):
        f = globals()['find_%s' % f]
    found = []
    unversioned = []
    mismatch = 0
    for item in f(**kwargs):
        ver = version_func(item)
        if ver is None:
            unversioned.append(item)
        elif version_below is None or ver < version_below:
            found.append((ver, item))
        else:
            mismatch += 1
    if found:
        found.sort()
        return found[-1][1]
    progname = None
    if 'progname' in kwargs:
        progname = kwargs['progname']
    elif f.__name__.startswith('find_'):
        progname = f.__name__[5:] or None
    if progname is None:
        progname = '<unknown>'
    if mismatch:
        raise VersionConstrained(progname)
    elif unversioned:
        raise VersionsUnknown(progname)
    else:
        raise ProgramNotFound(progname)

## -------------------------------------------------------[ data ... [

WINDOWS_ROOTS = ['%(windir)s',
                 '%(SystemRoot)s',
                 ]

## -------------------------------------------------------] ... data ]

## ----------------------------------------[ find_progs wrappers ... [

def find_PosixTool(progname,
                   indirs=0,
                   scanpath=1,
                   xroots=WINDOWS_ROOTS,
                   **kwargs):
    """
    use find_progs with appropriate defaults to find
    a generic Posix-compatible executable
    """
    if indirs == 0:
        indirs = PosixToolsDirs()
    return find_progs(progname=progname,
                      indirs=indirs,
                      scanpath=scanpath,
                      xroots=xroots,
                      **kwargs)

def find_svn(progname='svn',
             indirs=0,
             scanpath=1,
             **kwargs):
    """
    use find_progs with appropriate defaults to find an 'svn' executable
    """
    if indirs == 0:
        indirs = SubversionDirs()
    return find_progs(progname=progname,
                      indirs=indirs,
                      scanpath=scanpath,
                      **kwargs)

def find_tsvn(progname='TortoiseProc.exe',
              indirs=0,
              scanpath=1,
              **kwargs):
    """
    use find_progs with appropriate defaults to find a
    TortoiseSVN executable, by default: TortoiseProc.exe
    (will very likely succeed under Windows(tm) only)
    """
    if indirs == 0:
        indirs = ProgramDirs('TortoiseSVN/bin')
    return find_progs(progname=progname,
                      indirs=indirs,
                      scanpath=scanpath,
                      **kwargs)

def find_find(progname='find',
              **kwargs):
    """
    use find_progs with appropriate defaults to find a 'find' executable
    which does what a *x find is supposed to do
    """
    return find_PosixTool(progname=progname,
                          **kwargs)

def find_grep(progname='grep',
              indirs=0,
              scanpath=1,
              **kwargs):
    """
    use find_progs with appropriate defaults to find a 'grep' executable
    """
    if indirs == 0:
        indirs = PosixToolsDirs()
    return find_progs(progname=progname,
                      indirs=indirs,
                      scanpath=scanpath,
                      **kwargs)

def find_sed(progname='sed',
             **kwargs):
    """
    use find_progs with appropriate defaults to find a 'sed' executable
    """
    return find_PosixTool(progname=progname,
                          **kwargs)

def find_sort(progname='sort',
              **kwargs):
    """
    use find_progs with appropriate defaults to find a 'sort' executable
    which does what a *x sort is supposed to do
    """
    return find_PosixTool(progname=progname,
                          **kwargs)

def find_tar(progname='tar',
              **kwargs):
    """
    use find_progs with appropriate defaults to find a 'tar' executable

    NOTE: some tar implementations on Windows don't support filtering
          the output through gzip, bzip2, compress and the like; thus,
          it might be necessary to seek a bsdtar.exe as well.
          You can do this explicitly, of course, but there is no convenient
          automatic way do it automatically (yet).
    """
    return find_PosixTool(progname=progname,
                          **kwargs)

def find_uniq(progname='uniq',
              **kwargs):
    """
    use find_progs with appropriate defaults to find a 'uniq' executable
    """
    return find_PosixTool(progname=progname,
                          **kwargs)

def find_vim(progname='vim',
             indirs=0,
             scanpath=1,
             vdirs=0,
             **kwargs):
    """
    use find_progs with appropriate defaults to find a 'vim' executable
    """
    if indirs == 0:
        indirs = VimDirs()
    if vdirs == 0:
        vdirs = VimVDirs()
    return find_progs(progname=progname,
                      indirs=indirs,
                      scanpath=scanpath,
                      vdirs=vdirs,
                      **kwargs)

def find_gvim(progname='gvim',
              **kwargs):
    """
    look for gvim in the same places like (the console version) vim
    """
    return find_vim(progname=progname,
                    **kwargs)

def find_diff(progname='diff',
              indirs=0,
              scanpath=1,
              **kwargs):
    """
    use find_progs with appropriate defaults to find a 'diff' executable
    """
    if indirs == 0:
        indirs = DiffDirs()
    return find_progs(progname=progname,
                      indirs=indirs,
                      scanpath=scanpath,
                      **kwargs)

def find_ln(progname='ln',
            indirs=0,
            scanpath=1,
            **kwargs):
    """
    use find_progs with appropriate defaults to find an 'ln' executable
    which hopefully supports the important switches (-f, -s, ...)
    """
    if indirs == 0:
        indirs = PosixToolsDirs()
    return find_progs(progname=progname,
                      indirs=indirs,
                      scanpath=scanpath,
                      **kwargs)

def find_python(progname='python',
                indirs=0,
                scanpath=1,
                vdirs=0,
                **kwargs):
    """
    use find_progs with appropriate defaults to find a 'python' executable
    """
    if indirs == 0:
        indirs = PythonDirs()
    if vdirs == 0:
        vdirs = PythonVDirs()
    return find_progs(progname=progname,
                      indirs=indirs,
                      scanpath=scanpath,
                      vdirs=vdirs,
                      **kwargs)

def find_cvs(progname='cvs',
             indirs=0,
             scanpath=1,
             **kwargs):
    """
    use find_progs with appropriate defaults to find a 'cvs' executable
    """
    if indirs == 0:
        indirs = ProgramDirs('TortoiseCVS')
    return find_progs(progname=progname,
                      indirs=indirs,
                      scanpath=scanpath,
                      **kwargs)

# PuTTY suite (http://www.chiark.greenend.org.uk/~sgtatham/putty/):

def find_putty(progname='putty',
               indirs=0,
               scanpath=1,
               **kwargs):
    """
    use find_progs to find a PuTTY executable
    """
    if indirs == 0:
        indirs = ProgramDirs('PuTTY')
    return find_progs(progname=progname,
                      indirs=indirs,
                      scanpath=scanpath,
                      **kwargs)

def find_pscp(progname='pscp',
              **kwargs):
    """
    use find_putty to find pscp (PuTTY's scp client)
    """
    return find_putty(progname=progname,
                      **kwargs)

def find_psftp(progname='psftp',
              **kwargs):
    """
    use find_putty to find psftp (PuTTY's secure FTP client)
    """
    return find_putty(progname=progname,
                      **kwargs)

def find_plink(progname='plink',
              **kwargs):
    """
    use find_putty to find plink (PuTTY's commandline connection utility)
    """
    return find_putty(progname=progname,
                      **kwargs)

def find_pageant(progname='pageant',
                 **kwargs):
    """
    use find_putty to find pageant (PuTTY's authentication agent)
    """
    return find_putty(progname=progname,
                      **kwargs)

## ----------------------------------------] ... find_progs wrappers ]

## ---------------------------------------------[ ToolsHub class ... [

class ToolsHub(dict):
    """
    Provide a dictionary of tools.

    Allows to seek tools only when needed, and seek them only once.
    """
    def __init__(self, fallback=find_PosixTool, **kwargs):
        """
        Initialization:

          hub = ToolsHub()

        You may specify special functions to find
        certain programs, e.g.

          hub = ToolsHub(tar=[my_tar_finder,
                              {'scanpath': 0}],
                         sed={'indirs': ...})

        The ToolsHub will look for a find_sed function and fallback to
        find_PosixTool by default.
        """
        def interesting_name(s):
            return (s.startswith('__') and
                    s.endswith('__')
                    ) or 'get' in s or 'set' in s

        hintsmap = {}
        self.fallback = fallback
        for k, v in kwargs.items():
            if isinstance(v, dict):
                func, adic = self.smartie(k)
                adic.update(v)
            else:
                if isinstance(v, tuple):
                    v = list(v)
                else:
                    assert isinstance(v, list), \
                            'Only lists, tuples and dicts are ' \
                            'accepted (%r)' % (v,)
                try:
                    func = v.pop(0)
                except IndexError:
                    func, adic = self.smartie(k)
                if v:
                    bdic = v.pop(0)
                    assert isinstance(bdic, dict), \
                            'dictionary of arguments to function ' \
                            'expected (%r)' % (bdic,)
                    adic.update(bdic)
                    assert not v
            hintsmap[k] = (func, adic)
        self.hintsmap = hintsmap
        self.sequences = {}

    def __iter__(self):
        return self.__iter__.__dict__()

    def __getitem__(self, key):
        if key not in self.__dict__:
            try:
                f, kwargs = self.hintsmap[key]
            except KeyError:
                f, kwargs = self.smartie(key)
            seq = f(**kwargs)
            if seq:
                self.sequences[key] = seq.__iter__()
                val = seq.next()
                self.__dict__.__setitem__(key, val)
                return val
            else:
                self.__dict__.__setitem__(key, None)
        try:
            return self.__dict__.__getitem__(key)
        except KeyError:
            return None

    def smartie(self, progname):
        # TODO: find better name ...
        """
        Return a tuple (function, kwargs): a function and a dictionary of
        keyword arguments.  If the module contains a function
        "find_<progname>", it is returned; otherwise, the fallback is used
        (find_PosixTool by default), and <progname> is given as the keyword
        argument "progname".
        """
        try:
            return (globals()['find_'+progname],
                    {})
        except KeyError:
            return (self.fallback,
                    {'progname': progname,
                     })

    def __str__(self):
        return str(self.__dict__)

## ---------------------------------------------] ... ToolsHub class ]

## ---------------------------------------[ directory generators ... [

class WinProgramDirs(object):
    """
    Executable class as a helper for the ProgramFiles etc. environment
    variables of recent Windows (tm) operating systems
    """
    def __init__(self, env=None):
        self.used = 0
        if env is None:
            env = environ
        self.env = environ

    def __reinit(self):
        if not self.used:
            self.reinit()
            self.used = 1

    def __call__(self, *args):
        self.__reinit()
        if not args:
            for d in self.dirs():
                yield d
        for a in args:
            for d in self.dirs():
                da = abspath(join(d, a))
                yield da

    def reinit(self, dic=None):
        if dic is not None:
            self.env = dic
        vals = []
        for k, v in self.env.items():
            ku = k.upper()
            if (k.startswith('ProgramFiles')
                or k.startswith('ProgramW')
                or ku.startswith('PROGRAMFILES')
                or ku.startswith('PROGRAMW')
                ):
                v2 = abspath(v)
                if v2 not in vals:
                    vals.append(v2)
        self._dirs = vals

    def dirs(self):
        self.__reinit()
        for d in self._dirs:
            yield d

# yields generator functions:
ProgramDirs = WinProgramDirs()

def PosixToolsDirs():
    """
    Generate the directories to search for POSIX tools without a special
    generator function; used by find_PosixTool, if the indirs argument is
    0 (the default)
    """
    for d in ProgramDirs('GnuWin32/bin'):
        yield d
    # http://sourceforge.net/projects/unxutils/ 
    for p in [
            r'%(SystemDrive)s\Tools\UnxUtils',
            r'%(SystemDrive)s\UnxUtils',
            r'%(SystemDrive)s',
            ]:
        yield join(p, r'usr\local\wbin')

    for d in [
            # Tobias Herp's system:
            r'%(SystemDrive)s\Compiler\MinGW\msys\1.0\bin',
            # MinGW doesn't like to be installed in a path containing blanks ...
            r'%(SystemDrive)s\MinGW\msys\1.0\bin',
            r'%(HomeDrive)s\MinGW\msys\1.0\bin',
            ]:
        yield d
    # just to be sure:
    for d in ProgramDirs('MinGW/msys/1.0/bin'):
        yield d
    for d in CygwinDirs():
        yield d

def CygwinDirs():
    # Cygwin programs are best used in a Cygwin environment,
    # where they are found in the usual *x directories,
    # and expect *x filename conventions on Windows systems
    for d in [
            r'%(SystemDrive)s\Cygwin',
            r'%(HomeDrive)s\Cygwin',
            ]:
        yield d
    for d in ProgramDirs('Cygwin'):
        yield d

def SubversionServerDirs():
    """
    Generate the directories to search for a svnserve executable;
    might contain svn excutables as well, and thus included by the
    SubversionDirs function
    """
    yield '%(VISUALSVN_SERVER)s/bin'

def SubversionDirs():
    """
    Generate the directories to search for a svn executable;
    used by find_svn, if the indirs argument is 0 (the default)
    """
    for d in ProgramDirs('TortoiseSVN/bin'):
        yield d
    # server distributions:
    for d in SubversionServerDirs():
        yield d
    for d in PosixToolsDirs():
        yield d

def VimDirs():
    """
    Generate the directories to search for a vim executable;
    used by find_vim, if the indirs argument is 0 (the default);
    see VimVDirs()
    """
    yield '%(VIM_EXE_DIR)s'
    for d in PosixToolsDirs():
        yield d

def VimVDirs():
    """
    Generate the directories to search for a vim executable;
    used by find_vim, if the vdirs argument is 0 (the default)
    """
    for wpd in ProgramDirs():
        yield join(wpd, 'Vim', 'vim*')

def DiffDirs():
    """
    Generate the directories to search for a diff executable;
    used by find_diff, if the indirs argument is 0 (the default).
    """
    yield '%(VIM_EXE_DIR)s'
    for d in PosixToolsDirs():
        yield d

def PythonDirs():
    """
    Generate directories to search for a python executable;
    used by find_python, if the indirs argument is 0 (the default).
    Note: More important is the vdirs argument which is used first;
    see PythonVDirs!
    """
    yield '%(PYTHONHOME)s'
    for d in PosixToolsDirs():
        yield d

def PythonVDirs():
    """
    Generate directories to search for a python executable;
    used by find_python, if the vdirs argument is 0 (the default).
    """
    def gen_parents():
        for d in ['%(SystemDrive)s\\',    # default! :-(
                  r'%(SystemDrive)s\Interpreter',
                  r'%(SystemDrive)s\Interpreter\Python',
                  ]:
            yield d
        for d in ProgramDirs():
            yield d
    for wpd in gen_parents():
        yield join(wpd, 'python*')

## ---------------------------------------] ... directory generators ]

def _ffunc(topic, verbose=0, **kwargs):
    """
    demo:
    call the function for the given topic
    """
    from thebops.errors import err
    if topic == 'progs':
        err('use the --find-progs option instead')
        return
    elif topic == 'PosixTool':
        return
    try:
        f = globals()['find_'+topic]
        if verbose:
            print 'find_%s(%s):' \
                  % (topic, ('\n'+(6+len(topic))* ' '
                             ).join(['%s=%r' % tup
                                     for tup in fargs.items()]))
        else:
            print 'find_%s():' % topic
        for p in f(**kwargs):
            print '-', p
    except KeyError:
        err('sorry, no function find_%s'
            % topic)

if __name__ == '__main__':
    try:
        from thebops.enhopa import OptionParser, OptionGroup
    except ImportError:
        from optparse import OptionParser, OptionGroup
    from thebops.opo import add_version_option, add_verbosity_options
    p = OptionParser(description='find Posix-conforming tools,'
                     ' even on Win* systems')

    g = OptionGroup(p, "Demo options")
    g.add_option('--find',
                 action='append',
                 metavar=_('find,grep,...'),
                 help=_('use the special function find_find, find_grep '
                 'etc. to find the specified program'))
    g.add_option('--find-all',
                 action='store_true',
                 help=_('demonstrate all special find_... functions'))
    g.add_option('--find-progs',
                 action='append',
                 metavar=_('prog|cfg.ini|...'),
                 help=_('the program, script or config file to find, using'
                 ' the unwrapped find_progs function'))
    p.add_option_group(g)

    g = OptionGroup(p, "Options for find_... functions")
    h = OptionGroup(p, "hidden options")
    meta_dirseq = pathsep.join(('DIR1', 'DIR2', '...'))
    search_opts = []
    search_opts.append('parentsof')
    g.add_option('--parentsof',
                 action='store',
                 metavar=_('DIR'),
                 help=_('a directory which is searched first, and then all '
                 'files.'))
    search_opts.append('indirs')
    g.add_option('--indirs',
                 action='store',
                 metavar=meta_dirseq,
                 help=_('some directories to be looked in next, separated by '
                 '"%(pathsep)s". Environment '
                 'variables can be given in Python syntax (e.g. '
                 '"%%(HOME)s%(sep)sbin")'
                 ) % globals())
    search_opts.append('scanpath')
    g.add_option('--scanpath',
                 action='store',
                 dest='scanpath',
                 metavar=_('y[es]|n[o]'),
                 help=_('whether to scan the PATH'
                 ' (see also --pathvar)'))
    search_opts.append('xroots')
    g.add_option('--xroots',
                 action='store',
                 metavar=meta_dirseq,
                 help=_('root directories which contain inappropriate objects'
                 ' which should be ignored (syntax like --indirs)'))
    search_opts.append('pathvar')
    g.add_option('--pathvar',
                 action='store',
                 metavar='PATH',
                 help=_('the PATH-like environment variable which contains '
                 'directories, separated by "%(pathsep)s"'
                 ) % globals())
    # not implemented yet by find_progs(), is it?
    search_opts.append('inroots')
    h.add_option('--inroots',
                 action='store',
                 metavar=meta_dirseq,
                 help=_('root directories to search'
                 ' (NOT IMPLEMENTED YET)'
                 '; syntax like --indirs and --xroots. Since this can take a '
                 'very long time, it is done last.'))
    p.add_option_group(g)

    try:
        from thebops.modinfo import main as modinfo
        option, args = modinfo(version=__version__, parser=p)
    except ImportError:
        try:
            p.set_collecting_group()
        except AttributeError:
            pass
        option, args = p.parse_args()

    from thebops.errors import err, check_errors, info

    def makebool(raw):
        if raw is None:
            return raw
        if raw in ('0', '1'):
            return int(raw)
        if not raw:
            raise ValueError('(false/empty) %r not understood' % raw)
        s = raw.lower()
        if 'yes'.startswith(s):
            return 1
        if 'no'.startswith(s):
            return 0
        if 'true'.startswith(s):
            return 1
        if 'false'.startswith(s):
            return 0
        if s == 'on':
            return 1
        if s == 'off':
            return 0
        raise ValueError('boolean value "%s" not understood' % s)

    args_hint = 0
    if option.find_progs or option.find or option.find_all:
        fargs = dict()
        for k in search_opts:
            v = getattr(option, k)
            if v is None:
                continue
            if k in ('scanpath',
                     ):
                try:
                    fargs[k] = makebool(v)
                except ValueError, e:
                    err('--%(k)s: %(e)s' % locals())
            elif k in ('indirs', 'xroots',
                       'inroots',
                       ):
                fargs[k] = v.split(pathsep)
            else:
                fargs[k] = v
        args_hint = len(fargs) == 0
    else:
        boo = 0
        for k in search_opts:
            v = getattr(option, k)
            if v is not None:
                err('--%s: nothing to seek '
                    '(use one of --find, --find-all, --find-progs)' % k)
                boo = 1
        if not boo:
            err('nothing to do')

    if option.find_progs:
        progs = []
        for tmp in option.find_progs:
            progs.extend(tmp.split(','))
        first = 1
        for p in progs:
            if option.verbose:
                if first:
                    first = 0
                else:
                    print
                print 'find_progs(%s):' \
                      % ',\n           '.join(['%s=%r' % tup
                                               for tup in [('progname', p),
                                                   ]+fargs.items()])
            found = 0
            for f in find_progs(progname=p, **fargs):
                print '-', f
                found += 1
            if found:
                args_hint = 0
            else:
                err('%s not found' % p)
        if args_hint:
            info('hint: try at least one of %s'
                 % ', '.join(['--%s' % o
                              for o in ('parentof', 'indirs', 'scanpath',
                                        # 'pathvar', 'xroots',
                                        # 'inroots',
                                        )]))
        if option.find or option.find_all:
            print

    topics = []
    if option.find:
        for s in option.find:
            topics.extend(s.split(','))
    if option.find_all:
        for k in sorted([k[5:] for k in globals().keys()
                         if k.startswith('find_')]):
            if k == 'progs':
                continue
            elif k in topics:
                continue
            else:
                topics.append(k)
    first = 1
    for t in topics:
        if first:
            first = 0
        elif option.verbose:
            print
        _ffunc(t, verbose=option.verbose, **fargs)

    if args:
        err(_('non-option arguments are not supported; see %s'
              ) % ('--find',
                   ))
    check_errors()

