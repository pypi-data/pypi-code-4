"""
Home module for inspect/introspection based activities and helpers.
"""

import inspect
import ast
import codegen
# import astor
from mementos import MementoMetaclass, with_metaclass
from show.linecacher import *
import textwrap
from stuf import stuf
from say import fmt, FmtException

prefix = stuf(normal='', slot='/', superclass='^', baseobject='*')


# TODO: either update and include local version of codegen
# (see repo on ~/pytest/Git/codegen, but needs tests fixed)
# or switch to module like astor https://pypi.python.org/pypi/astor/0.2.1

DEBUGGING = False


class ClassProps(with_metaclass(MementoMetaclass)):

    """
    Memoized finder of class props.
    """

    def __init__(self, cls):
        self.cls = cls
        self.mro = inspect.getmro(cls)
        self.prefixes = self._findprops(cls)
        self.props = sorted(self.prefixes.keys())
        if cls is not object:
            already = set(self.props)
            cprops = ClassProps(self.mro[1])
            super_props = cprops.props
            already.update(super_props)
            self.props = sorted(already)
            for k, v in cprops.prefixes.items():
                if k not in self.prefixes:
                    self.prefixes[k] = prefix.superclass + v

    def _findprops(self, cls):
        """
        Get the properties of the given class. Follow the MRO up the chain,
        recursively, until ``object``
        """

        try:
            classkeys = list(cls.__dict__.keys())
        except AttributeError:
            classkeys = []

        try:
            slotkeys = list(cls.__slots__)
        except AttributeError:
            slotkeys = []

        char = prefix.baseobject if cls is object else prefix.normal
        # prefixes = { k: char for k in classkeys }
        prefixes = dict((k, char) for k in classkeys)

        # prefixes.update({ k: prefix.slot for k in slotkeys })
        prefixes.update(dict(k, prefix.slot) for k in slotkeys)

        return prefixes

    @property
    def prefixed(self):
        return [self.prefixes[p] + p for p in self.props]

    # TODO: finish code to do class-based discovery of props along the MRO
    # NOT sure what the prefixing is


def object_props(o):
    """
    Find the props of the given object. Its class properties are assumed
    immutable, but its own properties are assumed to be changeable at a moment's
    notice. Objects known to be proxy objects (e.g. for the SQLAlchemy ORM) need
    to be handled specially, because its class attributes have nothing to do
    with the attributes of the object they proxy.
    """

    try:
        proxyprops = getattr(o, '_sa_class_manager')
        # If did not fail, dealing with SQLAlchemy ORM proxy
        proxykeys = list(proxyprops.keys())
    except AttributeError:
        proxykeys = []

    if not proxykeys:
        try:
            proxyprops = getattr(o, '_get_current_object')
            # If did not fail, dealing with Flask proxy
            proxykeys = list(proxyprops())
        except AttributeError:
            proxykeys = []

    try:
        dictkeys = list(o.__dict__.keys())
    except AttributeError:
        dictkeys = []

    if proxykeys:
        # SQLAlchemy proxy objects special - don't try looking into the
        # class. Nothing useful there. It won't tell you what properties
        # of the proxied object are, just of the proxy class itself.
        # Counterproductive.
        slotkeys, classkeys = [], []
    else:
        t = type(o)
        try:
            slotkeys = list(t.__slots__)
        except AttributeError:
            slotkeys = []

        cprops = ClassProps(t)
        classkeys = cprops.props

    # prop_prefix = cprops.prefixes.copy()
    # prop_prefix.update({ k: prefix.normal for k in dictkeys })
    # prop_prefix.update({ k: prefix.slot for k in slotkeys })

    allprops = sorted(set(proxykeys + dictkeys + slotkeys + classkeys))

    if DEBUGGING:
        sd = set(allprops).symmetric_difference(dir(o))
        sdneat = sorted(s for s in sd if not s.startswith('__'))
        if sdneat:
            print("SOME PROP KEYS NOT FOUND EXCEPT BY DIR:",)
            print(sorted(sdneat),)
    return allprops


# TODO: better mechanism for dealing with mutability?
# perhaps check hash (or content); alternately, let clients declare that some
# classes are mutable - in which case, delete them from cache every use

def to_source(node):
    """
    Convert the given AST node back to Python source code.
    """
    return codegen.to_source(node)

    source = astor.to_source(node)

    # print "node:", node
    # print "source:", source

    # astor.to_source loves to wrap expressions in parenthesis, leading to
    # a mis-match with what seen in the input. This tries to reverse those
    # extra parens.
    if isinstance(node, ast.Module) and hasattr(node, 'body') and \
       len(node.body) == 1 and isinstance(node.body[0], ast.Expr):
        node = node.body[0]
    if isinstance(node, (ast.Expr, ast.BinOp, ast.UnaryOp)) and source.startswith('(') and \
        source.endswith(')'):
        source = source[1:-1]
    return source

    # TODO: More robust mapping of source string to source here. Possibly using
    # original string, but with AST parsing used as guideline to where that string
    # starts and stops.

class CallArgs(with_metaclass(MementoMetaclass, ast.NodeVisitor)):

    """
    An ``ast.NodeVisitor`` that parses a Python function call and determines its
    arguments from the corresponding AST. Memoized so that parsing and
    traversing the AST is done once and only once; subseqnet requests are
    delivered via cache lookup.
    """

    TARGET_FUNCS = set()  # function names we care about

    @classmethod
    def add_target_func(cls, name):
        """
        When inspecting ASTs, must know the name of the "show" functions
        to consider. E.g. 'show', 'show.items', 'show.dir' and so on.
        This function adds those names for a given base name.
        """
        suffixes = '.items .props .changed .dir .chars .local .watched'.split()
        suffixes.insert(0, '')
        names = [name + s for s in suffixes]
        cls.TARGET_FUNCS.update(names)

    def __init__(self, filepath, lineno):
        """
        Start a new CallArgs instance for a given filepath and lineno
        """
        ast.NodeVisitor.__init__(self)
        self.filepath = filepath
        self.lineno   = lineno
        self.source   = None  # placeholder
        self.ast      = None  # placeholder
        self.args     = None  # placeholder
        self.get_ast()
        self.visit(self.ast)

    def get_ast(self):
        """
        Find the AST. Easy if single source line contains whole line. May
        need a bit of trial-and-error if over multiple lines.
        """
        src = ""
        for lastlineno in range(self.lineno, self.lineno + 10):
            line = getline(self.filepath, lastlineno)
            if line is None:
                raise ArgsUnavailable('getline returns None at {lastlineno}')
            src += line
            try:
                srcleft = textwrap.dedent(src)
                self.ast = ast.parse(srcleft)
                self.source = src
                return
            except IndentationError:
                pass
            except SyntaxError:
                pass
        raise ParseError('Failed to parse source:\n{src}\n')

    def visit_Call(self, node):
        """
        Called for all ``ast.Call`` nodes. Collects source of each argument.
        Note that AST ``starargs`` and ``keywords`` properties are not
        considered. Because ``CallArgs`` parses just one line of source code out
        of its module's context, ``ast.parse`` assumes that arguments are
        normal, not ``*args``. And ``**kwargs`` we can ignore, because those are
        pragmas, not data.
        """

        def call_name(n):
            """
            Given an AST node n which we suspect might represent the name of a target
            callable (e.g. ``show`` or one of its attribute-define subcalls such as
            ``show.props``), return the name of the called function, if discoverable. If
            not one of the simple forms we typically see, return ``None``.
            """
            if isinstance(n.func, ast.Name):
                return n.func.id
            elif isinstance(n.func, ast.Attribute):
                a = n.func
                if isinstance(a.value, ast.Name):
                    return '.'.join([a.value.id, a.attr])
                else:
                    # could be an attribute of a call, but for those, we don't
                    # much care
                    return None
            else:
                return None

        name = call_name(node)
        if name in self.TARGET_FUNCS:
            self.args = [to_source(arg) for arg in node.args]
        else:
            # visit its children
            ast.NodeVisitor.generic_visit(self, node)

    def visit_Compare(self, node):
        """
        Called for all ``ast.Compare`` nodes, for ``show> something syntax``.
        Collects source of each argument.
        """

        def call_name_for_compare(n):
            """
            Given an AST node n which we suspect might represent the name of a target
            callable (e.g. ``show`` or one of its attribute-define subcalls such as
            ``show.props``), return the name of the called function, if discoverable. If
            not one of the simple forms we typically see, return ``None``.
            Very similar to the ``call_name`` of ``visit_Call``, except it accesses
            slightly different node attributes to reflect different AST types.
            """
            if isinstance(n, ast.Name):
                return n.id
            elif isinstance(n, ast.Attribute):
                if isinstance(n.value, ast.Name):
                    return '.'.join([n.value.id, n.attr])
                else:
                    # could be an attribute of a call, but for those, we don't
                    # much care
                    return None
            else:
                return None

        op = node.ops[0]
        if isinstance(op, ast.Gt):
            left, right = node.left, node.comparators[0]
            name = call_name_for_compare(left)
            if name in self.TARGET_FUNCS:
                self.args = [to_source(right)]
            else:
                # visit its children
                ast.NodeVisitor.generic_visit(self, left)
                ast.NodeVisitor.generic_visit(self, right)

    def visit_BinOp(self, node):
        """
        Called for all ``ast.Compare`` nodes, for ``show> something syntax``.
        Collects source of each argument.
        """

        def call_name_for_binop(n):
            """
            Given an AST node n which we suspect might represent the name of a target
            callable (e.g. ``show`` or one of its attribute-define subcalls such as
            ``show.props``), return the name of the called function, if discoverable. If
            not one of the simple forms we typically see, return ``None``.
            Very similar to the ``call_name`` of ``visit_Call``, except it accesses
            slightly different node attributes to reflect different AST types.
            """
            if isinstance(n, ast.Name):
                return n.id
            elif isinstance(n, ast.Attribute):
                if isinstance(n.value, ast.Name):
                    return '.'.join([n.value.id, n.attr])
                else:
                    # could be an attribute of a call, but for those, we don't
                    # much care
                    return None
            else:
                return None

        if isinstance(node.op, ast.RShift):
            left, right = node.left, node.right
            name = call_name_for_binop(left)
            if name in self.TARGET_FUNCS:
                self.args = [to_source(right)]
            else:
                # visit its children
                ast.NodeVisitor.generic_visit(self, left)
                ast.NodeVisitor.generic_visit(self, right)


    def visit_Assert(self, node):
        ast.NodeVisitor.generic_visit(self, node.test)

        # Previously did not need this generic visit for assert statements,
        # but at some point, tests started failing unless it was here.