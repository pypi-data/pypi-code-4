#-*- coding: utf-8 -*-
"""
    sphinx.domains.dqn
    ~~~~~~~~~~~~~~~~~~~

    The Dqn domain.

    :copyright: Copyright 2013 by Takesxi Sximada <takesxi.sximada@gmail.com>
    :license: BSD, see LICENSE for detail.
"""
import os
from docutils import nodes
from docutils.parsers.rst import directives

from sphinx import addnodes
from sphinx.locale import l_, _
from sphinx.domains import Domain
from sphinx.util.nodes import set_source_info
from sphinx.util.compat import Directive, make_admonition
from sphinx.directives.other import int_or_nothing
from sphinx.ext.todo import todo_node, Todo, TodoList

class DepthFilter(object):
    def __init__(self, base, depth):
        self.base = base
        self.depth = depth

    def is_valid(self, docname):
        if docname.startswith(self.base):
            name = docname.replace(self.base, '')
            if name.startswith('/'):
                name = name[1:]
            
            count = name.count('/')
            if count == 0:
                return True
            elif count == 1 and os.path.basename(name) == 'index':
                return True
        return False

class Tree(Directive):
    """
    """
    has_content = True
    required_arguments = 0
    optional_argments = 0
    final_argument_whitespace = False
    option_spec = {'maxdepth': int,
                   'glob': directives.flag,
                   'hidden': directives.flag,
                   'numbered': int_or_nothing,
                   'titlesonly': directives.flag,
                   }
    
    def run(self):
        env = self.state.document.settings.env
        suffix = env.config.source_suffix
        ret = []
        # (title, ref) pairs, where ref may be a document, or an external link,
        # and title may be None if the document's title is to be used
        entries = []
        includefiles = []
        all_docnames = env.found_docs.copy()

        # don't add the currently visited file in catch-all patterns
        all_docnames.remove(env.docname)
        rootdir = os.path.dirname(env.docname)

        rootdir = os.path.normpath(rootdir)
        if rootdir == '.':
            rootdir = ''

        docnames = all_docnames
        maxdepth = self.options.get('maxdepth', 1)
        depthfilter = DepthFilter(rootdir, maxdepth)
        docnames = filter(depthfilter.is_valid, docnames)

        for docname in sorted(docnames):
            all_docnames.remove(docname) # don't include it again
            entries.append((None, docname))
            includefiles.append(docname)
            if not docnames:
                ret.append(self.state.document.reporter.warning(
                        'toctree glob pattern %r didn\'t match any documents',
                        line=self.lineno))

        subnode = addnodes.toctree()
        subnode['parent'] = env.docname
        # entries contains all entries (self references, external links etc.)
        subnode['entries'] = entries
        # includefiles only entries that are documents
        subnode['includefiles'] = includefiles
        subnode['glob'] = True
        subnode['maxdepth'] = self.options.get('maxdepth', 1)
        subnode['hidden'] = 'hidden' in self.options
        subnode['numbered'] = self.options.get('numbered', 0)
        subnode['titlesonly'] = 'titlesonly' in self.options
        set_source_info(self, subnode)
        wrappernode = nodes.compound(classes=['toctree-wrapper'])
        wrappernode.append(subnode)
        ret.append(wrappernode)
        return ret


class DqnDomain(Domain):
    """The domain for dqn.
    """
    
    name = 'dqn'
    label = 'DQN'
    object_types = {}
    
    directives = {
        'tree': Tree,
        }
    
    roles = {}
    initial_data = {}
    indices = {}
    
def setup(app):
    app.add_domain(DqnDomain)
