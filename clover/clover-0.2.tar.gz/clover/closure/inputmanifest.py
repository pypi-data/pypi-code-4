from __future__ import absolute_import
import logging
import time
import os
from clover.solver import Solver
from clover.sourcefile import get_requirements_from_sourcefiles

logger = logging.getLogger('clover.manifest')


class InputManifest(object):
    """ Every "passenger" (sourcefile) for a build.
    """
    externs = None
    all_sourcefiles = None
    required_sourcefiles = None

    def __init__(self, required=None, all=None, externs=None):
        assert isinstance(required, set)
        assert isinstance(all, set)
        
        self.required_sourcefiles = required
        self.all_sourcefiles = all
        self.externs = None

    def have_sourcefiles_expired(self):
        return any(map(lambda sf: sf.is_cache_expired(), self.all_sourcefiles))
        
    def get_all_sourcefiles(self):
        return self.required_sourcefiles | self.all_sourcefiles

    def get_sorted_deps(self):
        """ Return a list of SourceFile in dependency order.
         
            self.input_sourcefiles requirements are used as the root of graph.
        """
        provides = list(get_requirements_from_sourcefiles(self.required_sourcefiles))
        start = time.time()
        logger.info("Inputs: %s", provides)
        tree = Solver(self.get_all_sourcefiles())
        logger.info('Calcdeps %s', time.time()-start)
        deps = tree.get_dependencies(provides)
        logger.info('Required: %s %s', len(deps), time.time()-start)
        deps+= list(self.required_sourcefiles)
        
        return deps
        #return list(reversed(sort_sourcefiles(deps)))

    def get_base_js(self):
        base = get_closure_base_file(self.get_all_sourcefiles())
        return base


def is_closure_base_file(sourcefile):
    """Returns true if the given _PathSource is the Closure base.js source."""
    if os.path.basename(sourcefile.path) != 'base.js':
        return False
    provides = sourcefile.get_provide_names()
    return len(provides) == 1 and 'goog' in provides


def get_closure_base_file(sources):
    """Given a set of sources, returns the one base.js file.
    
    Note that if zero or two or more base.js files are found, an error message
    will be written and the program will be exited.
    
    Args:
    sources: An iterable of _PathSource objects.
    
    Returns:
    The _PathSource representing the base Closure file.
    """
    base_files = filter(is_closure_base_file, sources)

    if not base_files:
        raise Exception('No Closure base.js file found.')

    if len(base_files) > 1:
        logger.error('More than one Closure base.js files found at these paths:')
        for base_file in base_files:
            logger.error(base_file.path)
        raise Exception('More than one Closure base.js files found.')
    return base_files[0]