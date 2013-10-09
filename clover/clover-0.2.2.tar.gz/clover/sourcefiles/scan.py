from __future__ import absolute_import
import os
import re
# Matches a .js file path.
from clover.config.baseconfig import logger
from clover.sourcefiles.javascript import JavascriptSourceFile
from clover.sourcefiles.soy import SoySourceFile

_SOURCE_FILE_REGEX = re.compile(r'^.+\.(js|soy)$')

TEST_FILES = re.compile(r'^.+_test\.(js|html)$')


def scan_for_test_files(root):
    """ Scans a directory tree for JavaScript files.
  
        Args:
            root: str, Path to a root directory.
        
        Returns:
            An iterable of paths to JS files, relative to cwd.
    """
    return scan_tree(root, path_filter=TEST_FILES)


def scan_for_source_files(root):
    """ Scans a directory tree for JavaScript files.
  
        Args:
            root: str, Path to a root directory.
  
        Returns:
            An iterable of paths to JS files, relative to cwd.
    """
    return scan_tree(root, path_filter=_SOURCE_FILE_REGEX)

# TODO: walk_filter
def scan_tree(root, path_filter=None, ignore_hidden=True):
    """Scans a directory tree for files.
  
    Args:
      root: str, Path to a root directory.
      path_filter: A regular expression filter.  If set, only paths matching
        the path_filter are returned.
      ignore_hidden: If True, do not follow or return hidden directories or files
        (those starting with a '.' character).
  
    Yields:
      A string path to files, relative to cwd.
    """

    def OnError(os_error):
        raise os_error

    for dirpath, dirnames, filenames in os.walk(root, onerror=OnError, followlinks=True):
        # os.walk allows us to modify dirnames to prevent decent into particular
        # directories.  Avoid hidden directories.
        for dirname in dirnames:
            if ignore_hidden and dirname.startswith('.'):
                dirnames.remove(dirname)

        
        for filename in filenames:
            
            # nothing that starts with '.'
            if ignore_hidden and filename.startswith('.'):
                continue

            fullpath = os.path.join(dirpath, filename)
            
            if path_filter and not path_filter.match(fullpath):
                continue

            yield os.path.normpath(fullpath)


def find_sourcefiles_in_paths(paths):
    possible_source_paths = set()
    for path in paths:
        logger.info('Scanning path %s', path)
        for i in scan_for_source_files(path):
            possible_source_paths.add(i)

    # TODO: refactor with below
    
    #logging.info("Sources: %s", pprint.pformat(possible_source_paths))
    sources = set()
    for path in possible_source_paths:
        if path.endswith('soy'):
            sources.add(SoySourceFile(path=path))
        elif path.endswith('js'):
            sources.add(JavascriptSourceFile(path=path))

    logger.info("Found %s source files from paths.", len(sources))
    return sources


def find_sourcefiles_from_inputs(inputs):
    sources = set()
    for path in inputs:
        # TODO: move these validations out of here
        if not os.path.exists(path):
            raise Exception("Input file '%s' doest not exist!" % path)
        
        if not os.path.isfile(path):
            raise Exception("Input file '%s' is a directory!" % path)
        
        if path.endswith('soy'):
            sources.add(SoySourceFile(path=path))
        elif path.endswith('js'):
            sources.add(JavascriptSourceFile(path=path))

    logger.info("Found %s source files from inputs.", len(sources))
    return sources