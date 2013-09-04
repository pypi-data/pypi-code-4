import os
import sys
import subprocess
from termcolor import colored
from tod.links import printable_status
from tod.links import expand
from tod.links import expand_source
from tod.links import status as link_status
from tod.links import UNLINKED
from tod.links import CONFLICT
from tod.links import MISSING
from tod.links import LINKED
from tod.links import MAX_STATUS

from pprint import pprint


def link(args):
    """Link the file/folder from the config repo to the filesystem."""
    dst = expand(args.mapping[args.section].get(args.name))
    src = expand_source(args.repo, args.name)
    if not dst:
        print colored('Unknown Link Name', 'yellow')
        sys.exit(1)
    s = link_status(src, dst)
    if s == UNLINKED:
        os.symlink(src, dst)
        print colored('OK', 'green')
    else:
        print colored(s, 'red')
        print "Unable to link %s --> %s" % (src, dst)
        sys.exit(1)


def link_all(args):
    """
    Iterate over all the possible configs and attempt to link them if their
    status is currently unlinked.
    """
    for name in args.mapping[args.section]:
        dst = expand(args.mapping[args.section].get(name))
        src = expand_source(args.repo, name)
        s = link_status(src, dst)
        if s == UNLINKED:
            os.symlink(src, dst)
            print colored('Linked: %s to %s' % (src, dst), 'green')
        elif s == LINKED:
            print colored('Skipped: %s' % src, 'yellow')
        elif s == MISSING:
            print colored('Source Missing: %s' % src, 'yellow')
        elif s == CONFLICT:
            print colored('Conflict: %s' % src, 'red')


def unlink(args):
    """Unlink the file/folder from the config repo to the filesystem."""
    dst = expand(args.mapping[args.section].get(args.name))
    src = expand_source(args.repo, args.name)
    if not dst:
        print colored('Unknown Link Name', 'yellow')
        sys.exit(1)
    s = link_status(src, dst)
    if s == LINKED:
        os.unlink(dst)
        print colored('OK', 'green')
    else:
        print colored(s, 'red')
        print "Unable to unlink %s --> %s" % (src, dst)
        sys.exit(1)


def status(args):
    """Display the status of all config mappings."""
    out = []
    for section, mapper in args.mapping.iteritems():
        out.append(section)
        out.append('-' * len(section))
        max_source = max([len(m) for m in mapper])
        for src, dst in mapper.iteritems():
            s = link_status(expand_source(args.repo, src), expand(dst))
            line = [
                printable_status(s.rjust(MAX_STATUS)),
                src.ljust(max_source),
                colored(' -> ', 'blue'),
                dst
            ]
            out.append(' '.join(line))
        out.append('\n')

    print '\n'.join(out)


def diff(args):
    """Check for config changes that need to be committed."""
    src = expand_source(args.repo)
    output = subprocess.check_output(['git', 'diff', '--stat'], cwd=src)
    if output:
        print output
    else:
        print colored('No uncommitted changes', 'green')
