#!/usr/bin/env python
# -*- coding: utf8 -*-
'''
    Buildit - (C) 2012-2013, Mike Miller
    A simple build tool for small projects.  License: GPL3+

    %%prog [options]
'''
if True:  # fold
    import sys, os, codecs
    from os import unlink
    from os.path import exists, splitext
    import traceback as tb
    from fnmatch import fnmatch
    from pprint import pformat

    from errors import (AttrMissing, BuildItError, CircularReference,
        ExecError, TargetDoesNotExist)
    from utils import (
        bold,
        dep_is_newer,
        execute,
        get_term_size,
        is_execattr,
        load_bldfile,
        ParsingError,
        print_wrapped,
        q,
    )

    __version__     = '0.81'
    shargs          = '-x -c'
    indent_txt      = '    '
    shargs          = '-x -c'
    indent          = '    '
    done            = []
    stderr          = sys.stderr
    shortcuts       = dict(py='python', pl='perl')

    #~ ireturn         = u'⏎'
    inote           = u'‣'
    iexc            = u'❗'
    iok             = u'✔'
    idir            = u'📂'
    ibld            = u'⚙'
    ierr            = u'✘'
    imove           = u'→'

    # support recursive runs, pipelines, bpython
    if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding is None:
        import locale
        sys.stdout = codecs.getwriter(locale.getdefaultlocale()[1])(sys.stdout)


def find_genrule(dep, genrules, opts):
    'If a generic rule matches, customize and build it.'
    rule = None
    for globstr in genrules:
        if fnmatch(dep, globstr):
            rule = genrules[globstr]
            break

    if rule:
        # prepare rule
        rule = rule.copy()
        if opts.verbose:
            print '\nGeneric rule:', dep, pformat(rule)

        basename = splitext(dep)[0]
        for key in rule:
            value = rule[key]
            if type(value) is list:
                value = [ v.replace('*', basename) for v in value ]
            else:
                value = rule[key].replace('*', basename)
            rule[key] = value

        if opts.verbose:
            print '\nRendered generic:', dep, pformat(rule), '\n'
    return rule


def check_rule(target, rules, genrules, opts, level=0):
    'Decide whether to build a target or not, then build it.'
    if opts.verbose: print 'Checking:', target
    if target in done:  return
    buildthis = False
    exitcodes = []
    rule = rules[target]

    # decide whether to build this one
    if exists(target):
        print indent * level + iok, target
    else:
        print indent * level + inote, target
        buildthis = True
    level += 1
    myindent = indent * level
    deps = rule.deps
    if deps:
        for dep in deps:
            # is dep a rule?
            if dep in rules:
                check_rule(dep, rules, genrules, opts, level=level)
            else:  # or a generic?
                genrule = find_genrule(dep, genrules, opts) # ?
                if genrule:
                    check_rule(dep, {dep: genrule}, [], opts, level=level)

            # is dep a file or missing?
            if dep_is_newer(target, dep):
                if dep not in done:         # some of this could be moved up
                    print myindent + iexc, dep
                buildthis = True  # could break here
            else:
                if dep not in done:
                    print myindent + iok, dep
    else:
        buildthis = True

    if buildthis:
        # find execopts, move pre to front; is_execattr ensures len(x) > 2
        execopts  =  sorted([ o  for o in rule.keys()  if is_execattr(o) ],
                            key=lambda x: x[1] != 'r')

        workdir = rule.workdir
        if workdir:
            origdir = os.getcwdu()
            if opts.verbose:
                print myindent + idir, 'cd', q(workdir)
            try:  os.chdir(workdir)
            except OSError, err:
                raise BuildItError(unicode(err))

        for execopt in execopts:
            shell = (execopt.split('.', 1)[1]  if '.' in execopt  else 'sh')
            shell = shortcuts.get(shell, shell)
            exitcodes.append(build(rule, execopt, level, opts, shell=shell))

        if workdir:
            if opts.verbose:
                print myindent + idir, 'cd', q(origdir)
            os.chdir(origdir)
    done.append(target)

    if opts.verbose:
        print '-' * 50
    return exitcodes # return buildthis , to save work?


def format_shellcode(code, delim):
    # rm leading blank line, escape single quotes, convert newlines
    # single quotes (' --> '\'')  http://stackoverflow.com/q/1250079/450917
    return code.lstrip().replace("'", r"'\''").replace('\n', delim)


def build(rule, execopt, level, opts, shell='sh'):
    ''' Build a given target. '''
    exitcode = EX_OK = os.EX_OK
    myindent = indent * level

    # build command line
    tempfile = rule.me_tmp_
    target = rule.me
    nsstr = 'me="%s"' % tempfile
    delim = ( '; ' if (opts.continue_block or shell in ('python', 'perl'))
                   else ' && ' )
    execstr = rule[execopt + '_tmp_']
    execstr = format_shellcode(execstr, delim)
    finalcmd = "%s %s %s '%s'" % (nsstr, shell, shargs, execstr)
    if opts.verbose:
        print myindent + ibld, 'env: ', nsstr
    print myindent + ibld, execopt + ':',
    if opts.verbose:
        print "%s -x -c '%s'" % (shell, execstr)
    else:
        print

    # rm tempfile, if it exists:
    try:  unlink(tempfile)
    except OSError: pass

    # run it
    cols, _ = get_term_size()  # enable indented wrapping of output
    subindent = myindent + indent
    cols = cols - len(subindent) - 1 # last col
    for line in execute(finalcmd):
        if type(line) is int:
            exitcode = line
        else:
            print_wrapped(line, subindent, cols)

    # move tempfile over destination atomically
    if exitcode == EX_OK:
        if exists(tempfile):   # race condition :/
            if opts.verbose:
                print myindent + ibld, 'move:', tempfile, imove, target,
            try:
                os.rename(tempfile, target)
                if opts.verbose:  print iok,
            except OSError, err:
                print myindent + ierr, 'file not moved:', err
            if opts.verbose: print

    # wrap up
    exitico = (ierr if exitcode else iok)
    print myindent + exitico + ' exit:', exitcode
    if exitcode:
        err = ExecError('Halting.')
        err.exitcode = exitcode
        raise err

    return exitcode


def main(args, opts):
    exitcode = os.EX_OK
    exitcodes = [exitcode]
    try:
        rules, genrules = load_bldfile(opts.filename)
        targets = rules.keys()
        if opts.verbose or opts.help:
            print 'Targets:\n    ',
            targs = [ k.encode('utf8') for k in targets ]
            print (bold(targs[0]) +',') if targs else '',
            print ', '.join(targs[1:]), '\n'
            if opts.help: return exitcode

        # validate bldfile
        if opts.skip_validation:
            if not rules:
                raise TargetDoesNotExist, 'No targets found.'
        else:
            validate_rules(rules, args, opts)

        # choose a target
        if args:  targets = args
        else:     targets = targets[:1]  # first only, like make

        # start building
        for target in targets:
            try:
                exitcodes += check_rule(target, rules, genrules, opts)
            except  (TargetDoesNotExist, AttrMissing, CircularReference), err:
                if opts.verbose:
                    tb.print_exc(file=stderr); print
                else:
                    cname = err.__class__.__name__
                    print >> stderr, '\nError: %s, %s\n' % (cname, err)
                if not opts.continue_targets:
                    break
        exitcode = max(exitcodes)

    except ExecError, err:
        if opts.verbose:
            tb.print_exc(file=stderr); print
        print >> stderr, '\n%s: %s\n' % (bold(err.__class__.__name__), err)
        if hasattr(err, 'exitcode'):
            exitcode = err.exitcode
        else:
            exitcode = os.EX_CONFIG

    except BuildItError, err:
        if opts.verbose:
            tb.print_exc(file=stderr); print
        print >> stderr, bold('Error') + ': %s' % err.message, '\n'
        exitcode = os.EX_DATAERR

    except ParsingError, err:
        print 'Parsing Error: %s' % err.message
        exitcode = os.EX_DATAERR

    return exitcode


def validate_rules(rules, args, opts):
    targets = rules.keys()
    if not targets:
        raise TargetDoesNotExist, 'No targets found.'

    for target, rule in rules.items():
        if opts.verbose:
            from pprint import pformat
            print 'Validating rule:', target, '\n', pformat(rule), '\n'

        if target in rule.get('deps', []):
            raise CircularReference, target + ', target may not be own dependency.'

        execopts = [ k  for k in rule.keys()  if is_execattr(k) ]
        for key in execopts:
            if key.startswith('exec'):
                break
        else:
            if not 'deps' in rule:
                raise AttrMissing, ('No (exec|dep) attrs in [%s].' % target)

    for arg in args:
        if arg not in targets:
            raise TargetDoesNotExist, "Rule [%s] doesn't exist." % arg

