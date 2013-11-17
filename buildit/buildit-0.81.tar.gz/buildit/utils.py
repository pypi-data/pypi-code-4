'''
    Buildit - (C) 2012-2013, Mike Miller
    A simple build tool for small projects.  License: GPL3+
'''
import os, sys, codecs, re
from os.path import exists, getmtime
from subprocess import Popen, STDOUT, PIPE
from cStringIO import StringIO
import ConfigParser as cp
from ConfigParser import (Error, InterpolationDepthError,
    InterpolationMissingOptionError, InterpolationSyntaxError,
    MAX_INTERPOLATION_DEPTH, NoOptionError, NoSectionError, SafeConfigParser)
from errors import DepDoesNotExist, TargetDoesNotExist, ReservedError

try:  from ushlex import split as shplit
except ImportError:
    try:  from shlex import split as shplit
    except ImportError:
        if sys.version < '3.0':
            print 'Warning: shlex module cannot handle unicode filenames,',
            print 'install ushlex.'

try:  from collections import OrderedDict
except ImportError:
    try:  from ordereddict import OrderedDict
    except ImportError:
        print 'Warning: targets not in order, install ordereddict.'
        sys.exit(1)


cp.DEFAULTSECT = 'vars'  # change default section name
delimiter = '%'
tmpsuffix = '.tmp'
execattr = re.compile(r'^(pre|post|)exec(\.[a-zA-Z0-9]+|)$') #, re.DEBUG)
class ParsingError(RuntimeError): pass


class AttrDict(dict):
    'A dict. that acts like an object, returns None if key/attr not found.'
    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, attr, value):
        self[attr] = value

    def copy(self):
        return AttrDict(self)


class BldConfigParser(SafeConfigParser):
    ''' A ConfigParser that uses string.Template for interpolation, rather
        than printf-style.
    '''
    _interpvar_re = re.compile(r'%{*([_\w][_\w0-9]*)}*', re.UNICODE)
    def _interpolate_some(self, option, accum, rest, section, _vars, depth):
        if depth > MAX_INTERPOLATION_DEPTH:
            raise InterpolationDepthError(option, section, rest)
        while rest:
            p = rest.find(delimiter)
            if p < 0:
                accum.append(rest)
                return
            if p > 0:
                accum.append(rest[:p])
                rest = rest[p:]
            # p is no longer used
            c = rest[1:2]
            if c == delimiter:
                accum.append(delimiter)
                rest = rest[2:]
            else:
                m = self._interpvar_re.match(rest)
                if m is None:
                    raise InterpolationSyntaxError(option, section,
                        'bad interpolation variable reference %r' % rest)
                var = self.optionxform(m.group(1))
                rest = rest[m.end():]
                try:
                    v = _vars[var]
                except KeyError:
                    raise InterpolationMissingOptionError(
                        option, section, rest, var)
                if delimiter in v:
                    self._interpolate_some(option, accum, v,
                                           section, _vars, depth + 1)
                else:
                    accum.append(v)

    def read_string(self, data):
        wrapper = codecs.getreader('utf8')(StringIO(data))
        self._read(wrapper, '<StringIO>') # 2nd arg: filename

    def readfp_utf8(self, filename):
        self.readfp(codecs.open(filename, 'r', 'utf_8_sig'))


def bold(text):
    'ansi bold text'
    return '\x1b[01m%s\x1b[00m' % text


def dep_is_newer(target, dep):
    'Return whether a dependency file is newer than a target file.'
    newer = False  # change to None
    if not exists(dep):
        raise DepDoesNotExist('Dependency file "%s" does not exist.' % dep)
    elif not exists(target):
        newer = True
    elif getmtime(dep) > getmtime(target):
        newer = True
    return newer


def execute(cmd, shell=True, echo=False):
    ''' Run process and return its output, one line at a time.
        the last item will be the integer return code.
    '''
    if echo:
        print 'exec:', cmd
    proc = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=shell)
    while True:
        line = proc.stdout.readline()
        if line:    yield line
        else:       break
    yield proc.wait()  # retcode


def extend(config, parent, target):
    'Copy properties of the parent to the given target.'
    parent_props = dict(config.items(parent, raw=True))
    target_props = config.options(target)
    for parent_prop in parent_props:
        if parent_prop not in target_props:
            config.set(target, parent_prop, parent_props[parent_prop])


def get_term_size():
    ''' Returns cols, lines
        http://stackoverflow.com/q/566746/450917
    '''
    import fcntl, termios, struct
    from os import environ as env
    def ioctl_GWINSZ(fd):
        try:
            cr = struct.unpack('hh', fcntl.ioctl(fd,termios.TIOCGWINSZ,'1234'))
        except:
            return None
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try: cr = ( env['COLUMNS'], env['LINES'])
        except:
            return None
    return int(cr[1]), int(cr[0])


def is_execattr(name):
    return execattr.match(name)


def load_bldfile(filename, from_string=None):
    rules, genrules = OrderedDict(), OrderedDict()
    try:
        config = BldConfigParser(dict_type=OrderedDict)
        config.optionxform = unicode  # case sensitive for unix
        if from_string:   config.read_string(from_string)
        else:             config.readfp_utf8(filename)     # skips BOM

        for target in config.sections():
            rule = AttrDict()  # rule object

            # check for extends
            try:
                parent = config.get(target, 'extends')  # pop
                config.remove_option(target, 'extends')
                extend(config, parent, target)
            except NoOptionError:  pass  # no extends
            except NoSectionError:
                raise TargetDoesNotExist(parent)

            # these loops should probably be done more efficiently...
            # raw
            items = config.items(target, raw=True, vars=dict(me=target))
            for name, value in items:
                if name.endswith('_'):
                    raise ParsingError('Attribute name may not end in ' +
                                'underscore: %s/%s' % (target, name))
                elif name == 'me' and value != target:
                    raise ReservedError('me cannot be set via attributes.' +
                                '%s/%s' % (target, name))
                rule[name + '_raw_'] = value

            # rendered, display
            items = config.items(target, vars=dict(me=target))
            for name, value in items:
                if name == 'deps':
                    value = shplit(value)
                rule[name] = value

            # rendered, temp
            items = config.items(target, vars=dict(me=target+tmpsuffix))
            for name, value in items:
                rule[name + '_tmp_'] = value

            if target.startswith('*.'):  # generic or not?
                genrules[target] = rule
            else:
                rules[target] = rule

    except Error, err:
        cname = err.__class__.__name__
        raise ParsingError, '%s: %s' % (cname, unicode(err))
    except ValueError, err:
        raise ParsingError, 'InterpolationSyntaxError: %s' % unicode(err)

    return rules, genrules


stdout_write = sys.stdout.write
def print_wrapped(text, myindent, cols):
    stdout_write(myindent + text[:cols])
    while len(text) > cols:     # wrapped
        text = text[cols:]
        stdout_write('\n' + myindent + text[:cols])


def q(text):
    if ' ' in text:
        return '"' + text + '"'
    else:
        return text

