import fnmatch
import os


def parse_ignore_file(lines):
    """
    some sanity check for ignore rules

    we dont and probably wont have anything close to .gitignore or .hgignore,
    we just have some basic globbing - since we run ignore rules on every
    file change we dont want to support everything.

    >>> parse_ignore_file(['#foo', '*.txt', '#comment', '*.txt', '*.f'])
    ['*.txt', '*.f']
    """
    ignore_rules = [] # we use a list because we want it ordered
    for ln in lines:
        if ln:
            if ln.startswith('!'):
                raise Exception('! not supported')
            if ln.startswith('^'):
                raise Exception('reg exp patterns are not supported')
            if ln.startswith('#'):
                continue
            if ln not in ignore_rules:
                ignore_rules.append(ln)
    return ignore_rules

def matches(path, pattern):
    """
    >>> matches(".kd-cache/", ".kd-cache/")
    True
    >>> matches(".kd-cache/foo.txt", ".kd-cache/*")
    True
    >>> matches(".kd-cache/foo.txt", ".kd-cache/")
    True
    >>> matches(".kd-cache/foo.txt", ".kd-cache/")
    True
    >>> matches(".kd-cache/bar/foo.txt", ".kd-cache/")
    True
    >>> matches(".kd-cache/foo.txt", ".kd-cache/*.py")
    False
    >>> matches(".kd-cache\\\\foo.txt", "*.txt")
    True
    >>> matches('.kd-cache\\\\foo.txt', ".kd-cache/")
    True
    """
    path = path.replace('\\', '/')
    if pattern.endswith(os.path.sep):
        pattern += '*'
    return fnmatch.fnmatchcase(path, pattern)


if __name__ == '__main__':
    assert matches(".kd-cache\\foo.txt", ".kd-cache/")
    
