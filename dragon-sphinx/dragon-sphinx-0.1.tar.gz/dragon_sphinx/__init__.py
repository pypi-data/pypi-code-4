"""
Sphinx extension defining the :dragon: domain.
"""
from collections import defaultdict

from sphinx import addnodes
from sphinx.roles import XRefRole
from sphinx.domains import Domain, ObjType, Index
from sphinx.directives import ObjectDescription
from sphinx.util.nodes import make_refnode
from sphinx.util.docfields import TypedField


class DragonTask(ObjectDescription):

    doc_field_types = [
        TypedField('input', label='Parameters', names=('input',),
            typenames=('input_type',)),
        TypedField('output', label='Output Values', names=('output',),
            typenames=('output_type',)),
        TypedField('files', label='Output Files', names=('file',),
            typenames=('file_type',)),
    ]

    def handle_signature(self, sig, signode):
        signode += addnodes.desc_name(sig, sig)
        signode['name'] = sig
        return sig

    def needs_arglist(self):
        return False

    def add_target_and_index(self, name, sig, signode):
        signode['names'].append(name)
        signode['ids'].append(name)
        self.env.domaindata['dragon']['task'][sig] = (self.env.docname,
                self.objtype)
        self.indexnode['entries'].append(('single', name + ' (task)', name, ''))


class DragonIndex(Index):

    name = 'dragontasks'
    localname = 'Dragon Tasks'
    shortname = 'dragon tasks'

    def generate(self, docnames=None):
        content = defaultdict(list)
        for name, info in self.domain.data['task'].items():
            content[name[0]].append((name, 0, info[0], name, '', '', info[1]))
        content = sorted(content.items(), key=lambda (k, v): k)
        return (content, True)


class DragonDomain(Domain):
    """
    Dragon domain.
    """

    name = 'dragon'
    label = 'Dragon'

    object_types = {
        'task': ObjType('task', 'task', 'obj'),
    }

    directives = {
        'task': DragonTask,
    }

    roles = {
        'task': XRefRole(),
    }

    initial_data = {
        'task': {},
    }

    indices = [DragonIndex]

    def clear_doc(self, docname):
        for typ in self.initial_data:
            for name, entry in self.data[typ].items():
                if entry[0] == docname:
                    del self.data[typ][name]

    def resolve_xref(self, env, fromdocname, builder, typ, target,
                     node, contnode):
        try:
            info = self.data[str(typ)][target]
        except KeyError:
            return
        else:
            title = typ.upper() + ' ' + target
            return make_refnode(builder, fromdocname, info[0], target,
                    contnode, title)

    def get_objects(self):
        for typ in self.initial_data:
            for name, entry in self.data[typ].iteritems():
                docname = entry[0]
                yield(name, name, typ, docname, typ + '-' + name, 0)


def setup(app):
    app.add_domain(DragonDomain)


