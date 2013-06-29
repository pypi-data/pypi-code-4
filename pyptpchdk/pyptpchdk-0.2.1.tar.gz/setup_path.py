import os
import sys

main_dir = os.path.split(__file__)[0]
if main_dir != '':
    os.chdir(main_dir)

# We expect exactly one directory name starting with 'lib'. Otherwise,
# it's hard to figure out where to expect the libraries.

try:
    lib_dirs = os.listdir('build')
except OSError, value:
    if str(value).find('No such file or directory') >= 0:
        print >>sys.stderr, (
            "Can't find build directory. Run 'setup.py build'.")
        sys.exit(1)
    else:
        raise
lib_dirs = [d for d in lib_dirs if d.startswith('lib')]
if len(lib_dirs) == 0:
    print >>sys.stderr, "Can't find libraries to test. Run 'setup.py build'"
    sys.exit(1)
if len(lib_dirs) > 1:
    print >>sys.stderr, "Found more than directory with built libraries."
    print >>sys.stderr, "Don't know which one to choose."
    sys.exit(1)

sys.path.insert(0, 'py')
sys.path.insert(0, os.path.join('build', lib_dirs[0]))
