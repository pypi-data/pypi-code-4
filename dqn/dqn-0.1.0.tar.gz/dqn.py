#! /usr/bin/env python
#-*- coding: utf-8 -*-
import re
import os
import abc
import sys
import pickle
import shutil
import hashlib
import optparse
import tempfile
import StringIO
import subprocess
#from xml.etree import ElementTree
import xml.etree.ElementTree
import lxml.etree

class ElementTree(object):
    _parser = lxml.etree.XMLParser(recover=True)
    ParseError = xml.etree.ElementTree.ParseError

    @classmethod
    def parse(cls, path):
        return lxml.etree.parse(path, cls._parser)

class DqnError(Exception):
    pass

class AnalyzeError(DqnError):
    pass

class NotFound(DqnError):
    pass

class NotSupportDomainType(DqnError):
    pass

def mkdir_p(path):
    try:
        os.makedirs(path)
    except BaseException:
        pass

def int_or_type_error(value):
    try:
        return int(value)
    except (ValueError, TypeError) as err:
        raise TypeError(value)

def call(line, background=False):
    stdout = tempfile.TemporaryFile()
    stderr = tempfile.TemporaryFile()
    
    child = subprocess.Popen(line, shell=True)
    if not background:
        child.wait()
    return child

path2ext = lambda path: os.path.splitext(path)[-1].strip('.').lower()

class Domain(object):
    _ext_domain = {'c': 'c',
                   'cpp': 'cpp',
                   'cxx': 'cpp',
                   'h': 'cpp',
                   'hpp': 'cpp',
                   'hxx': 'cpp',
                   'py': 'py',
                   'js': 'js',
                   'rst': 'rst',
                   'java': 'py',
                   }
    
    @classmethod
    def get(cls, path, directive):
        ext = path2ext(path)
        try:
            domain = cls._ext_domain[ext] # raise KeyError, is not support domain
        except KeyError as err:
            return 'py', directive
            raise NotSupportDomainType('Not support domain "{ext}" in {path}'.format(ext=ext,
                                                                                     path=path))
        if domain == 'cpp' and directive == 'var':
            domain = 'c'
        return domain, directive

class Location(object):
    """The source location data.
    """

    def __init__(self, path=None, line=None,
                 body=None, bodystart=None, bodyend=None,
                 ):
        self.path = None # file attribute
        self._line = None
        self.body = None # bodyfile attribute
        self._bodystart = None
        self._bodyend = None
        self.digest = None

    @property
    def line(self):
        return self._line

    @line.setter
    def line(self, value):
        self._line = int(value)

    @property
    def bodystart(self):
        return self._bodystart

    @bodystart.setter
    def bodystart(self, value):
        self._bodystart = int(value)

    @property
    def bodyend(self):
        return self._bodyend

    @bodyend.setter
    def bodyend(self, value):
        self._bodyend = int(value)

    @property
    def start(self):
        if self.path == self.body:
            return self.bodystart
        else:
            return self.line

    @property
    def end(self):
        if self.path == self.body:
            end = self.bodyend
            if end < 0:
                end += self.bodystart + 1
            return end
        else:
            return self.line + 1

    def calc(self):
        path = self.path
        start = self.start
        end = self.end
        
        with open(path, 'rb') as fp:
            lines = fp.readlines()
            lines = lines[start:end]
            buf = ''.join(lines)
            chksum = hashlib.md5(buf)
            self.digest = chksum.hexdigest()
        return self.digest

class LocationFactory(object):
    """The Location object creator.
    """

    def _create(self):
        """Return the Location object.
        """
        return Location()

    def from_tree(self, tree):
        """Return the locatino object, after travarse location etree object.
        
        example XML:

           <location file="FUNC_LOCATIONFILE" line="3"
                     bodyfile="FUNC_BODYFILE" bodystart="3" bodyend="6"/>
        """
        if tree is not None:
            name = tree.tag
            if name.lower() == 'location':
                loc = self._create()        
                loc.path = tree.get('file')
                loc.body = tree.get('bodyfile')
                loc.line = tree.get('line')                
                try:
                    loc.bodystart = tree.get('bodystart')
                    loc.bodyend = tree.get('bodyend')
                except (TypeError) as err:
                    print 'abnormal format xml.'
                    
                loc.calc()
                return loc
            raise ValueError('Illigal tag name (expect location): {0}'.format(name))
        raise ValueError('Illigal argument')

    def from_mdef(self, mdef):
        """Return the locatino object, after travarse memberdef etree object.
        
        example XML:

           <memberdef>
               <location file="FUNC_LOCATIONFILE" line="3"
                         bodyfile="FUNC_BODYFILE" bodystart="3" bodyend="6"/>
           </memberdef>
        """
        if mdef is not None:
            loctree = mdef.find('location')
            return self.from_tree(loctree)
        raise ValueError('Illigal argument')

class Directive(object):
    INDENT = 3
    def __init__(self):
        self.domain = None
        self.name = ''
        self.value = ''

        self._parent = None
        self.children = []

        self._bodystart = None
        self._bodyend = None
        self._indent = 0

        self.rststart = None
        self.rstend = None

        self.is_add = False
        self.is_update = False
        self.is_remove = False
        self.location = None

    @property
    def is_modify(self):
        return self.is_update or self.is_remove

    @property
    def digest(self):
        return self.location.digest
    
    @property
    def version(self):
        return ''
    
    def __str__(self):
        indent_space =  ' '*(self.layer*self.INDENT)
        if self.domain:
            name = '{0}:{1}'.format(self.domain, self.name)
        else:
            name = self.name


        buf = '{0}.. {1}:: {2}\n\n'.format(indent_space, name, self.value)
        
        change = None
        version = self.version
        if self.is_add:
            change = 'versionadded'
        elif self.is_update:
            change = 'versionchanged'
        elif self.is_remove:
            change = 'deprecated'

        if change:
            buf += '{indent}{nest}.. {change}:: {version}\n\n'.format(
                indent=indent_space, nest=' '*self.INDENT, change=change, version=version)
        return buf

    def __eq__(self, other):
        try:
            return self.parent == other.parent \
                and self.domain == other.domain \
                and self.name == other.name \
                and self.value == other.value
        except:
            return False

    def is_root(self):
        return not self.parent

    def append(self, child):
        self.children.append(child)
        child.parent = self

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, leaf):
        self._parent = leaf

    @property
    def layer(self):
        assert self.parent != self
        if self.parent:
            return self.parent.layer + 1 # nested 
        else:
            return 0 # root

    @property
    def indent(self):
        return self._indent

    @indent.setter
    def indent(self, value):
        self._indent = int_or_type_error(value)

    @property
    def bodystart(self):
        return self._bodystart

    @bodystart.setter
    def bodystart(self, value):
        self._bodystart = int_or_type_error(value)
    
    @property
    def bodyend(self):
        return self._bodyend

    @bodyend.setter
    def bodyend(self, value):
        value = int_or_type_error(value)
        if value == -1:
            self._bodyend = self.bodystart
        else:
            self._bodyend = value
    
    def calc_checksum(self):
        with open(self.path, 'rb') as fp:
            lines = fp.readlines()[self.bodystart:self.bodyend]
            data = ''.join(lines)
            hashmaker = hashlib.md5(data)
            self.checksum = hashmaker.hexdigest()

class DirectiveFactory(object):
    
    # Domain Directive Selector
    _kind_typ = {'public-func': 'method',
                 'public-static-attrib': 'attribute',
                 'function': 'function',
                 'variable': 'data',
                 'class': 'class',
                 'interface': 'class', # java
                 'enum': 'class', # java
                 'struct': 'type', # c
                 'typedef': 'type', # c
                 'union': 'type', # c
                 }

    def _create(self, parent=None):
        leaf = Directive()
        if parent:
            parent.append(leaf)
        return leaf

    def set_location(self, leaf, tree):
        """
        *tree* is memberdef tree.
        """
        loc_factory = LocationFactory()
        location = loc_factory.from_mdef(tree)
        leaf.location = location
        return location
    
    def from_mdef(self, tree, parent=None):
        leaf = self._create(parent)
        nametag = tree.find('name')
        if nametag is None:
            raise ValueError('Not found name tag.')
        leaf.value = nametag.text

        location = self.set_location(leaf, tree)
        
        kind = tree.get('kind')
        try:
            typ = self._kind_typ[kind]
        except KeyError:
            raise ValueError('Not support kind: {0}'.format(kind))

        if leaf.parent and\
                leaf.parent.name == 'class' and\
                typ == 'function':
            typ = 'method'

        domain, directive = Domain.get(location.path, typ)
        leaf.domain = domain
        leaf.name = directive
        return leaf

    def from_cdef(self, tree, parent=None):
        leaf = self._create(parent)
        nametag = tree.find('compoundname')
        if nametag is None:
            raise ValueError('Not found name tag.')
        leaf.value = nametag.text.split('::')[-1]

        location = self.set_location(leaf, tree)        
        
        kind = tree.get('kind')
        try:
            typ = self._kind_typ[kind]
        except KeyError:
            raise ValueError('Not support kind: {0}'.format(kind))

        if leaf.parent and\
                leaf.parent.name == 'class' and\
                typ == 'function':
            typ = 'method'

        domain, directive = Domain.get(location.path, typ)
        leaf.domain = domain
        leaf.name = directive
        return leaf

class DirectiveContainer(list):

    def roots(self):
        for directive in self:
            if not directive.parent:
                yield directive

    def subtree(self, branch):
        yield branch
        for leaf in branch.children:
            for child_leaf in self.subtree(leaf):
                yield child_leaf
    
    def tree(self):
        for root in self.roots():
            for leaf in self.subtree(root):
                yield leaf

    def search(self, leaf):
        for my_leaf in self.tree():
            if my_leaf == leaf:
                return my_leaf

class DirectiveStack(object):
    def __init__(self):
        self._core = []

    def push(self, elm):
        self._core.append(elm)

    @property
    def current(self):
        try:
            return self._core[-1]
        except IndexError:
            return None

    def pop(self):
        return self._core.pop() # raise IndexError

    @property
    def indent(self):
        try:
            return self.current.indent
        except AttributeError: # if self.current is None -> top
            return 0
        
def calc_checksum(path):
    def _wrap():
        with open(path, 'rb') as fp:
            lines = fp.readlines()
            directive = yield
            while True:
                start = directive.bodystart
                end = directive.bodyend
                data = ''.join(lines[start:end])
                hashobj = hashlib.md5(data)
                directive = yield hashobj.hexdigest()

    generator = _wrap()
    generator.next() # first is dust data
    return generator
        
class VirtualDirectiveParser(object):

    def __init__(self, path=None):
        self.path = path

    def parse(self, path=None):
        if path:
            self.path = path
        return self._parse()

    @property
    def directory(self):
        return os.path.dirname(os.path.abspath(self.path))

class XMLParser(VirtualDirectiveParser):
    def _parse(self):
        return DirectiveContainer(
            [directive for directive in self.iterparse()])

    def iterparse(self):
        path = self.path
        funcs = self.parse_class, self.parse_function, self.parse_variable
        alreadies = list()
        for nsfile in self.file2namespaces(path):
            namespace = self.path2tree(nsfile)
            for func in funcs:
                for directive in func(namespace):
                    if not directive in alreadies:
                        alreadies.append(directive)
                        yield directive

    def parse_xml(self, path):
        print path
        try:
            return ElementTree.parse(path)
        except:
            print 'Ooops!!:', path
            raise

    def path2tree(self, path_or_tree, use_attrs=['find', 'findall']):
        for attr in use_attrs:
            if not hasattr(path_or_tree, attr):
                path = path_or_tree
                return self.parse_xml(path)
        else:
            return path_or_tree

    def file2namespaces(self, filexml):
        """Convert file xml path to namespace xml path.

        dqn2_8py.xml -> namespacedqn2.xml
        """
        yield filexml
        xml_dir = os.path.dirname(os.path.abspath(filexml))
        tree = self.path2tree(filexml)
        cdef = tree.find('compounddef')
        if cdef is not None:
            for innernamespace in cdef.findall('innernamespace'):
                filename = innernamespace.get('refid') + '.xml'
                namespacexml = os.path.join(xml_dir, filename)
                if os.path.isfile(namespacexml):
                    yield namespacexml
                else:
                    print 'WARNING', namespacexml, 'is not found.'
                    
    def _parse_file(self, path):
        for namespacexml in self.filexml2namespacexml(path):
            yield self.parse_namespace(nsref)

    def _parse_namespace(self, path):
        tree = self.parse_xml(path)
        cdef = tree.find('compounddef')
        if cdef is not None:
            for leaf in self.parse_function(cdef):
                yield leaf

            for leaf in self.parse_variable(cdef):
                yield leaf                

    def get_compounddef(self, tree):
        return tree.find('compounddef')

    def generate_memberdefs(self, tree):
        cdef = self.get_compounddef(tree)
        for section in cdef.findall('sectiondef'):
            for memberdef in section.findall('memberdef'):
                yield memberdef

    def get_location(self, mdef):
        factory = LocationFactory()
        loc = factory.from_mdef(mdef)
        return loc.path, loc.bodystart, loc.bodyend

    def get_domain_directive(self, mdef, typ):
        path, start, end = self.get_location(mdef)
        ext = os.path.splitext(path)[-1].strip('.').lower()
        return Domain.get(path, typ)

    def parse_variable(self, namespace):
        factory = DirectiveFactory()
        for memberdef in self.generate_memberdefs(namespace):
            kind = memberdef.get('kind')
            if 'variable' == kind:
                yield factory.from_mdef(memberdef)
            
    def parse_function(self, namespace):
        factory = DirectiveFactory()
        for memberdef in self.generate_memberdefs(namespace):
            kind = memberdef.get('kind')
            if 'function' == kind:
                yield factory.from_mdef(memberdef)

    def generate_class(self, namespace):
        cdef = self.get_compounddef(namespace)
        for innerclass in cdef.findall('innerclass'):
            filename = innerclass.get('refid') + '.xml'
            class_xml = os.path.join(self.directory, filename)
            yield self.path2tree(class_xml)

    def parse_class(self, namespace):
        factory = DirectiveFactory()
        parse_childrens = self.parse_attribute, self.parse_method
        for class_tree in self.generate_class(namespace):
            cdef = self.get_compounddef(class_tree)
            leaf = factory.from_cdef(cdef)
            yield leaf

            for parse_children in parse_childrens:
                for child in parse_children(cdef, leaf):
                    yield child

    def generate_sectiondef(self, cdef, kinds=['.*']):
        reg_kinds = map(re.compile, kinds)
        for secdef in cdef.findall('sectiondef'):
            secdef_kind = secdef.get('kind')
            for regx in reg_kinds:
                if regx.match(secdef_kind):
                    yield secdef

    def generate_memberdef(self, *args, **kwds):
        for secdef in self.generate_sectiondef(*args, **kwds):
            for memberdef in secdef.findall('memberdef'):
                yield memberdef

    def _parse_attribute_and_method(self, name, cdef, kinds, parent=None):
        factory = DirectiveFactory()
        for memberdef in self.generate_memberdef(cdef, kinds):
            yield factory.from_mdef(memberdef, parent)
        
    def parse_attribute(self, cdef, parent=None):
        kinds = ['public-static-attrib']
        for directive in self._parse_attribute_and_method('attribute', cdef,
                                                          kinds, parent):
            yield directive
            
    def parse_method(self, cdef, parent=None):
        kinds = ['public-func']
        for directive in self._parse_attribute_and_method('method', cdef,
                                                          kinds, parent):
            yield directive

class RSTParser(VirtualDirectiveParser):
    REGX_DIRECTIVE = re.compile(
        '^\s*..\s+(?P<domain_directive>\S+)::\s+(?P<value>.*)')

    REGX_INDENT = re.compile('^(?P<indent>\s*)')
    
    def _parse(self):
        path = self.path
        with open(path, 'rb') as fp:
            return self.parsefp(fp)

    def parsefp(self, fp):
        directives = DirectiveContainer()
        stack = DirectiveStack()
        before_line = None
        for lineno, line in enumerate(fp):
            if len(line.strip()): # ignore blank lines.
                indent = self.get_indent(line)
                try:
                    while stack.indent >= indent:
                        if stack.current:
                            stack.current.rstend = lineno
                        stack.pop()
                except (IndexError, AttributeError) as err: # top directive
                    pass
                directive = self.get_directive(line)
                if directive:
                    directive.indent = indent
                    directive.rststart = lineno
                    if stack.current:
                        stack.current.append(directive)
                    directives.append(directive)                        
                    stack.push(directive)
        return directives
        
    def is_directive(self, line):
        return self.REGX_DIRECTIVE.search(line)

    def get_indent(self, line):
        match = self.REGX_INDENT.search(line)
        if match:
            return len(match.group('indent'))
        else:
            return 0

    def get_directive(self, line):
        match = self.is_directive(line)
        if match:
            indent = self.get_indent(line)
            domain_directive = match.group('domain_directive')
            if ':' in domain_directive:
                domain, directive = domain_directive.split(':')[:2]
            else:
                domain = None
                directive = domain_directive
            value = match.group('value')

            leaf = Directive()
            leaf.domain = domain
            leaf.name = directive
            leaf.value = value
            return leaf
        else:
            return None

class EditableBuffer(StringIO.StringIO):
    def __init__(self, name, mode='rb'):
        #super(EditableBuffer, self).__init__(ff.read())
        StringIO.StringIO.__init__(self)        
        self.mode = mode
        self.name = name
        
        try:
            with open(self.name, mode) as ff:
                self.write(ff.read())
        except IOError as err:
            pass
        self.seek(0)

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwds):
        self.close(*args, **kwds)
        
    def close(self, *args, **kwds):
        self.seek(0)
        mkdir_p(os.path.dirname(self.name))
        with open(self.name, 'w+b') as ff:
            ff.write(self.read())

    def clean_write(self, data, truncate=0):
        self.truncate(truncate)
        self.write(data)

class DoxyManager(object):

    def __init__(self, src_root):
        self.attr_value = {'INPUT': src_root,
                           'RECURSIVE': 'YES',
                           'GENERATE_XML': 'YES',
                           'GENERATE_HTML': 'NO',
                           'GENERATE_LATEX': 'NO',
                           }

    def configure(self, doxyfile='Doxyfile'):
        call('doxygen -g {0}'.format(doxyfile))
        regx_value = \
            dict(map(lambda (attr, value): (re.compile('^(?P<attr>{0})\s*='.format(attr)), value),\
                         self.attr_value.items()))
        
        with EditableBuffer(doxyfile) as fp:
            buf = StringIO.StringIO()
            for line in fp:
                for regx, value in regx_value.items():
                    match = regx.search(line)
                    if match:
                        line = match.group('attr') + ' = ' + value + '\n'
                        break
                buf.write(line)
            fp.truncate(0)
            buf.seek(0)
            fp.write(buf.read())

    def make(self):
        call('doxygen')

class HgManager(object):
    IGNOREFILE = '.hgignore'

    REGEXP_DEFAULTS = [r'.*~$',
                       r'.*\.orig',
                       r'.*\.bk$',
                       r'.*\.bak',
                       r'.*\.pyc',
                       r'.*\.tmp$',
                       r'.*\.log$',
                       r'.*\.pickle',
                       ]
    GLOB_DEFAULTS = [r'xml/*',
                     r'_build/*',
                     ]

    def __init__(self, regexp_patterns=None, glob_patterns=None):
        self._regexps = []
        self._globs = []

        if regexp_patterns is None:
            regexp_patterns = self.REGEXP_DEFAULTS
        if glob_patterns is None:
            glob_patterns = self.GLOB_DEFAULTS
        
        for pattern in regexp_patterns:
            self.add_regexp(pattern)
        for pattern in glob_patterns:
            self.add_glob(pattern)
    
    def init(self):
        return call('hg init')

    def add_regexp(self, pattern):
        regx = re.compile(pattern)
        self._regexps.append(regx)

    def add_glob(self, pattern):
        self._globs.append(pattern)

    def create_hgignore(self):
        if not os.path.exists(self.IGNOREFILE):
            with open(self.IGNOREFILE, 'w+b') as fp:
                fp.write('syntax: regexp\n')
                for regx in self._regexps:
                    pattern = regx.pattern
                    fp.write(pattern+'\n')
                fp.write('syntax: glob\n')                    
                for pattern in self._globs:
                    fp.write(pattern+'\n')                    

class SphinxManager(object):
    def configure(self):
        call('sphinx-quickstart')
        with EditableBuffer('conf.py') as fp:
            for line in fp:
                if 'sphinxcontrib.dqndomain' in line:
                    break
            else:
                fp.write("\nextensions.append('sphinxcontrib.dqndomain')\n")
                fp.write("html_theme = 'sphinxdoc'")

    def make(self, mode='html'):
        call('make {0}'.format(mode))

class DoxyPathAnalyzer(object):
    def generate_dirxmls(self, path):
        regx = re.compile('^dir_.*\.xml$')
        for name in filter(regx.search, os.listdir(path)):
            yield os.path.join(path, name)

    def analyze(self, xml):
        for xmlfile in self.generate_dirxmls(xml):
            for _srcfile, _xmlfile in self.analyze_dirxml(xmlfile):
                yield _srcfile, _xmlfile

    def analyze_dirxml(self, xmlfile):
        xmldir = os.path.dirname(xmlfile)
        tree = ElementTree.parse(xmlfile)

        dirnames = xmldir.split('/')
        ignore_dirs = ['.hg', '.git']
        for ignore_dir in ignore_dirs:
            if ignore_dir in dirnames:
                return
            
        tag_cdef = tree.find('compounddef')
        if tag_cdef is not None:
            tag_location = tag_cdef.find('location')
            if tag_location is not None:
                srcfile = tag_location.get('file')
                srcdir = os.path.dirname(srcfile)
                yield srcfile, xmlfile
            else:
                raise AnalyzeError()

            for tag_inner in tag_cdef.findall('innerfile'):
                refxmlname = tag_inner.get('refid')
                refsrcname = tag_inner.text
                if refxmlname and refsrcname:
                    refsrcfile = os.path.join(srcdir, refsrcname)
                    refxmlfile = os.path.join(xmldir, refxmlname + '.xml')
                    yield refsrcfile, refxmlfile,
                else:
                    print 'WARNING: Illigal xml schema: {0}'.format(xmlfile)
        else:
            raise AnalyzeError()

class Exchanger(object):
    def __init__(self, src, xml, rst):
        _ = os.path.abspath
        self.xml = _(xml)
        self.src = _(src)
        self.rst = _(rst)
        self.src_xml_rst = []

    def parse(self):
        analyzer = DoxyPathAnalyzer()
        for srcfile, xmlfile in analyzer.analyze(self.xml):
            self.append(srcfile, xmlfile)
                 
    def append(self, srcfile, xmlfile):
        _ = lambda path, root: os.path.relpath(os.path.abspath(path), root)
        relxml = _(xmlfile, self.xml)
        relsrc = _(srcfile, self.src)
        if os.path.isdir(srcfile):
            relrst = os.path.join(relsrc, 'index.rst')
        elif not relsrc.endswith('.rst'):
            relrst = relsrc + '.rst'
        else:
            relrst = relsrc
        self.src_xml_rst.append((relsrc, relxml, relrst))

    def absjoin(self, dirname, basename):
        return os.path.abspath(os.path.join(dirname, basename))

    def rel(self, name, base):
        return os.path.relpath(name, base)

    def abssrc(self, path):
        return self.absjoin(self.src, path)

    def absxml(self, path):
        return self.absjoin(self.xml, path)

    def absrst(self, path):
        return self.absjoin(self.rst, path)

    def _convert_file(self, path, ques_ans, abs_ques, abs_ans):
        path = os.path.abspath(path)
        for ques, ans in ques_ans:
            if path == abs_ques(ques):
                return abs_ans(ans)
        raise NotFound(path)

    def src2xml(self, path):
        iterator = ((src, xml) for src, xml, rst in self.src_xml_rst)
        return self._convert_file(path, iterator, self.abssrc, self.absxml)

    def xml2src(self, path):
        iterator = ((xml, src) for src, xml, rst in self.src_xml_rst)
        return self._convert_file(path, iterator, self.absxml, self.abssrc)

    def src2rst(self, path):
        iterator = ((src, rst) for src, xml, rst in self.src_xml_rst)
        return self._convert_file(path, iterator, self.abssrc, self.absrst)

    def rst2src(self, path):
        iterator = ((rst, src) for src, xml, rst in self.src_xml_rst)
        return self._convert_file(path, iterator, self.absxml, self.abssrc)

    def xml2rst(self, path):
        iterator = ((xml, rst) for src, xml, rst in self.src_xml_rst)
        return self._convert_file(path, iterator, self.absxml, self.absrst)

    def rst2xml(self, path):
        iterator = ((rst, xml) for src, xml, rst in self.src_xml_rst)
        return self._convert_file(path, iterator, self.absrst, self.absxml)

    def generate_src_xml_rst(self, abspath=False):
        for src, xml, rst in self.src_xml_rst:
            if abspath:
                src = self.abssrc(src)
                xml = self.absxml(xml)
                rst = self.absrst(rst)
            yield src, xml, rst

    @property
    def sphinxroot(self):
        return os.path.dirname(os.path.abspath(self.rst))

class Editor:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def edit(self, fp, **kwds):
        print 'EDIT:', fp.name

class EncodeEditor(Editor):
    def edit(self, fp, **kwds):
        now = fp.tell()
        regx = re.compile('\-\*\-\s+coding\:\s+utf\-8\s+\-\*\-')
        fp.seek(0)
        line = fp.readline()
        if not regx.search(line):
            fp.seek(0)
            buf = fp.read()
            fp.clean_write('.. -*- coding: utf-8 -*-\n\n')
            fp.write(buf)
            
PATTERN_TITLE = """(?P<open>\*+)\s*
(?P<title>.*)
(?P<close>\*+)\s*
"""
REGX_TITLE = re.compile(PATTERN_TITLE, re.M)

class TitleEditor(Editor):
    def __init__(self, rst_root):
        self.rst_root = rst_root

    def edit(self, fp, **kwds):
        if not self.get_title(fp):
            print '{0:20} {1}'.format('EDIT TITLE:', fp.name)
            name = os.path.basename(fp.name)
            if name == 'index.rst': # directory description
                title = os.path.dirname(fp.name)
            else:
                title = fp.name[:-4]
            title = title.replace(self.rst_root, '')
            if title == '':
                title = 'Source Code Tree'
            
            if title.startswith('/'):
                title = title[1:]
            self.add_title(fp, title)

    def get_title(self, fp):
        fp.seek(0)
        match = REGX_TITLE.search(fp.read())
        if match:
            return match.group('title').strip()

    def skip_encoding_setting(self, fp):
        fp.seek(0)
        
        while True:
            if fp.readline().strip() == '':
                break
        
    def add_title(self, fp, title):
        self.skip_encoding_setting(fp)
        now = fp.tell()
        buf = fp.read()
        bar = '*'*(len(title)+10) + '\n'
        fp.truncate(now)
        
        fp.write(bar)
        fp.write(title + '\n')
        fp.write(bar+'\n')
        fp.write(buf)

class TreeEditor(Editor):
    def edit(self, fp, **kwds):
        if fp.name.endswith('index.rst') and not self.has_tree(fp):
            fp.write('\n\n')
            fp.write('.. dqn:tree::')
            fp.write('\n\n')
            
    def has_tree(self, fp):
        regx = re.compile('^\.\.\s+dqn\:tree\:\:')
        fp.seek(0)
        for line in fp:
            if regx.search(line):
                return True

class DirectiveEditor(Editor):
    def __init__(self, exchanger):
        self.exchanger = exchanger

    def get_directives(self, fp):
        regx = re.compile('\.\.\s+(?P<name>\S+)\:\:\s+(?P<param>.*)')
        fp.seek(0)
        for line in fp:
            mtc = regx.search(line)
            if mtc:
                yield mtc.group('name'), mtc.group('param')

    def sorting(self, directives, rst_directives):
        for leaf in directives:
            if leaf.is_root():# new tree -> last 
                pass
            else:# aleady exist tree -> seach to add line no
                pass

    def edit(self, *args, **kwds):
        try:
            return self.editfp(*args, **kwds)
        except TypeError as err:
            raise

    def editfp(self, fp, **kwds):
        fp.seek(0)
        rst_parser = RSTParser()
        rst_directives = rst_parser.parsefp(fp)

        xmlfile = self.exchanger.rst2xml(fp.name)
        print xmlfile
        xml_parser = XMLParser(xmlfile)
        xml_directives = xml_parser.parse()

        pickle_path = os.path.join('_pickle', os.path.relpath(xmlfile)) + '.pickle'
        if os.path.isfile(pickle_path):
            with open(pickle_path, 'rb') as old_leaf_fp:
                old_leafs = pickle.load(old_leaf_fp)
                for now_leaf in xml_directives.tree():
                    old_leaf = old_leafs.search(now_leaf)
                    if old_leaf:
                        if old_leaf.digest != now_leaf.digest:
                            now_leaf.is_update = True
                    else:
                        now_leaf.is_add = True

        mkdir_p(os.path.dirname(pickle_path))
        with open(pickle_path, 'w+b') as old_leaf_fp:
            pickle.dump(xml_directives, old_leaf_fp)

        def _view(directive):
            if directive.parent:
                _view(directive.parent)
            print directive

        fp.seek(0)
        lines = fp.readlines()

        new_tree = []
        no_leaf = []

        for xml_leaf in xml_directives.tree():
            rst_leaf = rst_directives.search(xml_leaf)
            if rst_leaf:
                no = rst_leaf.rststart
                assert no is not None, '???'
                no_leaf.append((no, xml_leaf))
            else: # new directive
                if xml_leaf.is_root(): # add to last line
                    new_tree.append(xml_leaf)
                else:
                    parent_leaf = rst_directives.search(xml_leaf.parent)
                    if parent_leaf:
                        no = parent_leaf.rstend
                        assert no is not None, '???'
                        no_leaf.append((no, xml_leaf))
                    else:
                        new_tree.append(xml_leaf)

        no_leaf.sort(reverse=True)
        for no, leaf in no_leaf:
            line = str(leaf)
            if leaf.is_modify:
                lines[no] = line
        for leaf in new_tree:
            lines.append(str(leaf))
            
        fp.seek(0)
        fp.truncate()
        fp.writelines(lines)

    def _edit(self, fp, **kwds): # not use
        param_directive = dict([(param, name)
                                for name, param in self.get_directives(fp)])
        
        rst = fp.name
        xml = self.exchanger.rst2xml(rst)
        try:
            tree = ElementTree.parse(xml)
        except ElementTree.ParseError as err:
            print 'Oops!!:', xml
            raise
        cdef = tree.find('compounddef')

        fp.read() # seek to last

        if cdef is not None:
            # class
            for innerclass in cdef.findall('innerclass'):
                classref = self.exchanger.absxml(innerclass.get('refid') + '.xml')

                if not os.path.isfile(classref): # assert
                    print "!? Is it no exist why? Perhaps, doxygen's bug?: {0} by {1}".format(classref, xml)
                    break
                
                classtree = ElementTree.parse(classref)
                ccdef = classtree.find('compounddef')
                if ccdef is not None:
                    tag = ccdef.find('compoundname')
                    if tag is not None:
                        name = tag.text.strip()
                        name = name.split('::')[-1]
                        if not name in param_directive:
                            fp.write('\n\n.. py:class:: {0}'.format(name))
            
            # function and valiable
            print '*'*300
            for innernamespace in cdef.findall('innernamespace'):
                nsref = self.exchanger.absxml(innernamespace.get('refid') + '.xml')
                nstree = ElementTree.parse(nsref)
                ccdef = nstree.find('compounddef')
                if ccdef is not None:
                    for section in ccdef.findall('sectiondef'):
                        for memberdef in section.findall('memberdef'):

                            kind = memberdef.get('kind')
                            if 'variable' == kind:
                                nametag = memberdef.find('name')
                                if nametag is not None:
                                    name = nametag.text
                                    if not name in param_directive:
                                        fp.write('\n\n.. py:data:: {0}'.format(name))
                            elif 'function' == kind:
                                nametag = memberdef.find('name')
                                if nametag is not None:
                                    name = nametag.text
                                    if not name in param_directive:
                                        fp.write('\n\n.. py:function:: {0}'.format(name))

                            else:
                                print 'not suport:', kind

class IndexRstBuilder(object):
    def build(self, path, src_root=None):
        src_root = src_root if src_root else path

        editors = TreeEditor()
            
        for root, dirs, files in os.walk(path):
            _index = os.path.join(root, 'index.rst')
            if not os.path.isfile(_index):
                with EditableBuffer(_index) as fp:
                    editor.edit(fp)

class Processor(object):
    XML_DEFAULT = 'xml'
    RST_DEFAULT = 'source'

    def run(self, src, xml=None, rst=None):
        xml = xml if xml is not None else self.XML_DEFAULT
        rst = rst if rst is not None else self.RST_DEFAULT
        
        exchanger = Exchanger(src, xml, rst)
        doxymgr = DoxyManager(exchanger.src)
        hgmgr = HgManager()
        sphinxmgr = SphinxManager()

        hgmgr.init()
        hgmgr.create_hgignore()
        sphinxmgr.configure()
        doxymgr.configure()
        doxymgr.make()        

        exchanger.parse()

        editors = [EncodeEditor(),
                   TitleEditor(exchanger.rst),
                   TreeEditor(),
                   DirectiveEditor(exchanger),
                   ]

        for srcfile, xmlfile, rstfile \
                in exchanger.generate_src_xml_rst(abspath=True):
            dirname = os.path.dirname(rstfile)
            mkdir_p(dirname)
            
            if srcfile.endswith('.rst'):
                if not os.path.exists(rstfile):
                    shutil.copy(srcfile, rstfile)
                else:
                    pass  # do not copy if file exist.
            else:
                with EditableBuffer(rstfile) as fp:
                    for editor in editors:
                        editor.edit(fp)
        # source top rst
        editors = [EncodeEditor(),
                   TitleEditor(exchanger.rst),
                   TreeEditor(),
                   ]
        for root, dirs, files in os.walk(exchanger.rst):
            _path = os.path.join(root, 'index.rst')
            with EditableBuffer(_path) as fp:
                for editor in editors:
                    editor.edit(fp)

        # top rst
        editor = TreeEditor()
        with EditableBuffer('index.rst') as fp:
            editor.edit(fp)


class Cmd(object):
    verbosity = 1
    description = 'Documentation Template Generator'
    usage = 'usage: %prog [options] soure_directory'
    parser = optparse.OptionParser()
    
    def __init__(self, argv, quiet=False):
        self.quiet = quiet
        self.opts, self.args = self.parser.parse_args(argv[1:])

    def run(self):
        src = xml = rst = None
        args = self.args
        try:
            src = args[0]
            xml = args[1]
            rst = args[2]
        except IndexError as err:
            print err

        if src is None:
            self.error('Invalid paramter: Input a path to source code directory root.')

        processor = Processor()
        processor.run(src, xml, rst)
        
    def error(self, *args, **kwds):
        return self.parser.error(*args, **kwds)

def main(argv=sys.argv, quiet=False):
    cmd = Cmd(argv, quiet)
    cmd.run()

if __name__ == '__main__':
    main()
