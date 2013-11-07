# Copyright (c) 2013 Zeid Zabaneh
# PyTemplates is distributed under the terms of the GNU General Public License

from pytemplates.utils import escape
from pytemplates.utils import render_empty_tag
from pytemplates.utils import render_content
from collections import defaultdict
import re


def macro(f):
    setattr(f, 'template_macro', True)
    return f


def block(f):
    setattr(f, 'template_block', True)
    return f


def tag(arg, *args, **kwargs):
    _name = re.compile('^(\w+?)(?:\.|#|\:|$)')
    _classes = re.compile('\.([a-zA-Z0-9\-_]+)')
    _id = re.compile('\#(\w+)')
    _unnamed_attrs = re.compile('\:(\w+)')
    _named_attrs = re.compile('\[(\w+)="(.+)"\]')

    name = _name.findall(arg)[0]
    attributes = dict()
    tag_id = _id.findall(arg)
    tag_classes = _classes.findall(arg)
    tag_unnamed_attrs = _unnamed_attrs.findall(arg)
    tag_named_attrs = _named_attrs.findall(arg)

    unnamed_attributes = tag_unnamed_attrs
    named_attributes = {k: v for k, v in tag_named_attrs}
    if tag_id:
        attributes['id'] = tag_id[0]

    classes = ' '.join(tag_classes)

    if classes:
        attributes['_class'] = classes

    attributes.update(named_attributes)
    attributes.update(kwargs)
    unnamed_attributes += args

    return Tag(name, *unnamed_attributes, **attributes)


def render(variable, *args):
    if 'safe' in args:
        return variable
    else:
        return escape(variable.__str__())


class Tag(object):
    def __init__(self, tag_name, *args, **kwargs):
        self.tag_name = tag_name
        self.attributes = {k: v for k, v in kwargs.iteritems()}
        self.unnamed_attributes = [v for v in args]
        for k in self.attributes:
            if k[0] == '_':
                self.attributes[k[1:]] = self.attributes[k]
                del(self.attributes[k])


class Blocks(object):
    pass


class Macros(object):
    pass


class Tags(object):
    def __getattr__(self, name):
        return lambda *args, **kwargs: Tag(name, *args, **kwargs)


class Template(object):
    def __init__(self, dd=True, *args, **kwargs):
        self.doctype = "html"

        if hasattr(self, 'extra_macros'):
            for macro in self.extra_macros:
                setattr(self, macro.__name__, macro)

        self.context = defaultdict(str) if dd else dict()
        self.blocks = Blocks()
        self.macros = Macros()
        self._register_macros()
        self._register_blocks()

    def _register_blocks(self):
        members = ((k, getattr(self, k)) for k in dir(self) if
                   getattr(getattr(self, k), 'template_block', None))
        for k, v in members:
            setattr(self.blocks, k.lower(), v(*self._prepare()))

    def _register_macros(self):
        members = ((k, getattr(self, k)) for k in dir(self) if
                   getattr(getattr(self, k), 'template_macro', None))
        for k, v in members:
            setattr(self.macros, k.lower(), v)

    def template(self):
        pass

    def _context(self, context):
        for k, v in context.iteritems():
            self.context[k] = v

    def _prepare(self):
        # t = Tags()
        c = self.context
        b = self.blocks
        m = self.macros
        return c, b, m

    def include(self, file_name):
        f = open(file_name, 'r')
        string = f.read()
        return string

    def render(self, context=None):
        if context:
            self._context(context)
        template = self.template(*self._prepare())
        output = render_content(*template)
        if self.doctype:
            t = Tags()
            output = render_empty_tag(
                getattr(t, '!DOCTYPE')(self.doctype)) + output
        return output
