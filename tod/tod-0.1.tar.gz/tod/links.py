import os
from termcolor import colored

MISSING = 'missing'      # Source file is missing
CONFLICT = 'conflict'    # Existing file at destination that is not the source
UNLINKED = 'unlinked'    # source exists and destination is free
LINKED = 'linked'        # the source is already linked to the destination
UNKNOWN = 'unknown'      # huh?

MAX_STATUS = max(len(s) for s in [
    MISSING,
    CONFLICT,
    UNLINKED,
    LINKED,
])

def expand(path):
    return os.path.expanduser(os.path.expandvars(path))

def expand_source(repo, name=''):
    return expand(os.path.join(repo, 'files', name))

def _check_source_location(src):
    """Check the mapping to see that all source material exists"""
    return os.path.exists(src)

def _check_destination_linked(src, dst):
    if os.path.exists(dst):
        if os.path.samefile(src, dst):
            return True
    return False

def _check_destination_conflict(src, dst):
    if os.path.exists(dst):
        if not os.path.islink(dst):
            # Path Should be linked but not.
            return True
        if os.path.samefile(src, dst):
            # Path is a link, and points to the correct location.
            return False
        else:
            # Path is a link, but does not point to the correct location.
            return True
    return False

def status(src, dst):
    if not _check_source_location(src):
        return MISSING
    if _check_destination_conflict(src, dst):
        return CONFLICT
    if not _check_destination_linked(src, dst):
        return UNLINKED
    else:
        return LINKED

def printable_status(s):
    """Because termcolor messes with line length, need to look for status in
    the string.
    """
    if MISSING in s:
        return colored(s, 'red')
    if CONFLICT in s:
        return colored(s, 'yellow')
    if UNLINKED in s:
        return colored(s, 'magenta')
    if LINKED in s:
        return colored(s, 'green')
