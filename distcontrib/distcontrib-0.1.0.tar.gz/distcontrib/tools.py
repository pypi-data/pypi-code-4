#!/usr/bin/env python

""" Created on 14 Jun 2013 """
""" $Id: $ """

from distutils.extension import Extension

def exclude_files():
    '''List file name patterns to be excluded'''
    return ['*.pyc', '*.so', '*$py.class',
            '.project', '.classpath', '*.iws', '*.ipr',
            '*~', '.*', '*.bak']


def exclude_directories():
    '''List directory name patterns to be excluded'''
    return ['.*', 'CVS', '_darcs', '__pycache__',
            '.project', '.classpath',
            'nbproject', '.idea'
            'build', 'dist', 'EGG-INFO', '*.egg-info']


def exclude_data_files():
    '''List file name patterns to be excluded'''
    return ['*.py', '*.pxd', '*.c'] + exclude_files()


def exclude_data_directories():
    '''List directory name patterns to be excluded'''
    return exclude_directories()


def exclude_source_files():
    '''List file name patterns to be excluded'''
    return ['*.pxd', '*.c'] + exclude_files()


def exclude_python_source_files():
    '''List file name patterns to be excluded'''
    return ['*.py'] + exclude_source_files()


def exclude_source_directories():
    '''List directory name patterns to be excluded'''
    return exclude_directories()


def read(filename):
    '''Read filename and return its contents as a long string'''
    import codecs
    with codecs.open(filename, 'r') as f:
        data = f.read()
    return data


def __is_package(path):
    import os
    return (
        os.path.isdir(path) and
        os.path.isfile(os.path.join(path, '__init__.py')))


def __load_vars(path):
    '''This function loads ``name=value`` pairs where value is interpreted as
    a simple string value.

    ..note: This funtion is very restricted at this time.
    '''
    vars = {}
    with open(path, 'r') as f:
        for line in f:
            index = line.find('=')
            if index < 0:
                continue
            name = line[:index].strip()
            value = line[index + 1:].strip()
            vars[name] = str(value[1:-1])  # assumes it is a string declaration
    #print(vars)
    return vars


def find_package_files(
        package,
        exclude_files=[],
        exclude_directories=[],
        only_in_packages=False,
        recursive=True,
        show_ignored=False,
        base=None):
    '''Returns a dictionary which contains a single entry, identified by
    ``package`` and which contains a list of files, obtained by traversing
    ``base`` directory
    and optionally excluding files or directories.

    :param package: package name to be returned as key to the dictionary.

    :param base: base directory to be visited.

    :param exclude_files: files matching any pattern in this list are excluded.

    :param exclude_directories: Directories matching any pattern in this
    parameter will be ignored.

    :param recursive: when true, subdirectories are visited recursively.

    :param show_ignored: when true, then all the files that aren't
    included in package data are shown on stderr (for debugging purposes).

    :note patterns use wildcards, or can be exact paths (including
    leading ``./``), and all searching is case-insensitive.
    '''
    import os
    import sys
    import collections
    from fnmatch import fnmatchcase
    from distutils.util import convert_path

    def name_matches(name, kind, patterns):
        for pattern in patterns:
            if (fnmatchcase(name, pattern)):
                if show_ignored:
                    print(sys.stderr, '%s %s ignored by pattern %s'
                          % (kind, fn, pattern))
                return True
        return False

    result = collections.OrderedDict()
    if base is None:
        base = package.replace('.', '/')
    stack = [(convert_path(base), package, only_in_packages)]
    while stack:
        base, package, only_in_packages = stack.pop(0)
        is_package = __is_package(base)
        for name in os.listdir(base):
            fn = os.path.join(base, name)
            if os.path.isdir(fn):
                if recursive:
                    if name_matches(name, 'Directory', exclude_directories):
                        continue
                    stack.append((fn, package, only_in_packages))
            else:
                if only_in_packages and not is_package:
                    continue
                if name_matches(name, 'File', exclude_files):
                    continue
                result.setdefault(package, []).append(fn)
    return result


def find_package_sources(
        package,
        exclude_files=exclude_source_files(),
        exclude_directories=exclude_source_directories(),
        only_in_packages=True,
        show_ignored=False,
        base=None):
    '''This function is a shortcut to
           ``find_package_files(package, base,
                                exclude_source_files(),
                                exclude_source_directories())``

    >>> from setuptools import find_packages
    >>> import distcontrib.tools as tools
    >>> packages=find_packages()
    >>> for package in packages:
    ...     tools.find_package_sources(package)
    ...
    OrderedDict([('distcontrib', ['distcontrib/__init__.py', 'distcontrib/tools.py', 'distcontrib/bootstrap.py'])])
    OrderedDict([('distcontrib.command', ['distcontrib/command/__init__.py', 'distcontrib/command/zap.py', 'distcontrib/command/doctest.py'])])

    '''
    return find_package_files(package=package, base=base,
                              exclude_files=exclude_files,
                              exclude_directories=exclude_directories,
                              only_in_packages=only_in_packages,
                              recursive=False,
                              show_ignored=show_ignored)


def find_package_data(
        package,
        exclude_files=exclude_data_files(),
        exclude_directories=exclude_data_directories(),
        only_in_packages=False,
        show_ignored=False,
        base=None):
    '''This function is a shortcut to
            ``find_package_files(package, base,
                                 exclude_data_files(),
                                 exclude_data_directories())``
    '''
    return find_package_files(package=package, base=base,
                              exclude_files=exclude_files,
                              exclude_directories=exclude_directories,
                              only_in_packages=only_in_packages,
                              show_ignored=show_ignored)


def findall_package_sources(
        packages,
        exclude_files=exclude_source_files(),
        exclude_directories=exclude_source_directories(),
        only_in_packages=True,
        show_ignored=False,
        base=None):
    import collections
    result = collections.OrderedDict()
    for package in packages:
        result.update(
            find_package_sources(package, base,
                                 exclude_files=exclude_files,
                                 exclude_directories=exclude_directories,
                                 only_in_packages=only_in_packages,
                                 show_ignored=show_ignored))
    return result


def findall_package_data(
        packages,
        exclude_files=exclude_data_files(),
        exclude_directories=exclude_data_directories(),
        only_in_packages=True,
        show_ignored=False,
        base=None):
    import collections
    result = collections.OrderedDict()
    for package in packages:
        result.update(
            find_package_data(package, base=base,
                              exclude_files=exclude_files,
                              exclude_directories=exclude_directories,
                              only_in_packages=only_in_packages,
                              show_ignored=show_ignored))
    return result


def __as_module(filename):
    index = filename.find('.')
    if index < 0:
        return filename
    else:
        return filename[:index]


def find_ext_modules(
        packages,
        exclude_files=exclude_python_source_files(),
        exclude_directories=exclude_source_directories(),
        only_in_packages=True,
        show_ignored=False,
        base=None):
    '''Returns a list of *Extension* objects, suitable for *ext_modules*.

    >>> from setuptools import find_packages
    >>> import distcontrib.tools as tools
    >>> packages=find_packages()
    >>> EXT_MODULES=tools.find_ext_modules(packages)
    >>> for extension in EXT_MODULES:
    ...     print extension.sources

    :param packages: list of package names to be looked at.

    :param include: files matching any pattern in this list are include.

    :param show_ignored: when true, then all the files that aren't
    included in package data are shown on stderr (for debugging purposes).

    :note patterns use wildcards, or can be exact paths (including
    leading ``./``), and all searching is case-insensitive.
    '''
    result = []
    for package in packages:
        sources = find_package_sources(package=package, base=base,
                                       exclude_files=exclude_files,
                                       exclude_directories=exclude_directories,
                                       only_in_packages=only_in_packages,
                                       show_ignored=show_ignored)
        for dummy, files in sources.items():
            for file in files:
                print(file)
                result.append(Extension(__as_module(file), [file]))
    return result


def findfile(base='.', names=[], topdown=True, recursive=True, kind=None):
    '''Unix-style find command.

    >>> def printall(items):
    ...     for item in items:
    ...         print(item)
    ...
    >>> import distcontrib.tools as tools
    >>> printall( tools.findfile(kind='f', names=["*.pyc"], topdown=False) )
    ./distcontrib/command/zap.pyc
    ./distcontrib/command/__init__.pyc
    ./distcontrib/command/doctest.pyc
    ./distcontrib/tools.pyc
    ./distcontrib/__init__.pyc
    >>> printall( tools.findfile(base='build', topdown=False) )
    build/lib/distcontrib/command/doctest.py
    build/lib/distcontrib/command/zap.py
    build/lib/distcontrib/command/__init__.py
    build/lib/distcontrib/bootstrap.py
    build/lib/distcontrib/tools.py
    build/lib/distcontrib/command
    build/lib/distcontrib/__init__.py
    build/lib/distcontrib
    build/lib
    build
    >>> printall( tools.findfile(base='dist') )
    >>> printall( tools.findfile(base='*.egg-info') )

    '''
    def match(path, names):
        from fnmatch import fnmatchcase
        if names is None or len(names) == 0:
            return True
        fn = os.path.basename(path)
        for name in names:
            if (fnmatchcase(fn, name)):
                return True
        return False

    import os
    import glob
    result = list()
    f = (kind is None or kind=='f')
    d = (kind is None or kind=='d')
    stack = glob.glob(base)
    while stack:
        path = stack.pop(0)
        # print('**** ', path)
        if os.path.isfile(path):
            if f and match(path, names):
                # print('file ', path)
                result.append(path)
        elif recursive and os.path.isdir(path):
            if d and match(path, names):
                # print('dir  ', path)
                result.append(path)
            for item in os.listdir(path):
                stack.append(os.path.join(path,item))
    if not topdown:
        result.reverse()
    return result

#if __name__ == '__main__':
#    for item in findfile(names=['__pycache__']):
#        print item
    
