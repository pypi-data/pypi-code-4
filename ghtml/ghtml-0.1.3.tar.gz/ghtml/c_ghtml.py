# -*- encoding: utf-8 -*-
""" GHtml GObj
A gobj that generates html.

.. autoclass:: GHtml
    :members: start_up

"""
from mako.template import Template
from mako.runtime import Context
from mako.exceptions import TopLevelLookupException

from ginsfsm.gobj import (
    GObj,
)

from ginsfsm.compat import (
    NativeIO,
    tostr,
    iteritems_,
)
from ginsfsm.gconfig import add_gconfig

void_elements = [
    'area',
    'base',
    'br',
    'col',
    'command',
    'embed',
    'hr',
    'img',
    'input',
    'keygen',
    'link',
    'meta',
    'param',
    'source',
    'track',
    'wbr',
]

# Supported attributes.
GHTML_GCONFIG = {
    'debug': [bool, False, 0, None, 'Debugging mode'],
    'template': [str, '', 0, None, "Template name."],
    'extra_template': [str, '', 0, None, "Extra Template."],

    'tag': [str, '', 0, None, "The element type."],
    'attrib': [
        dict, {}, 0, None,
        "A dictionary containing the element's attributes."
    ],
    'text': [str, '', 0, None, "Data associated with the element."],
}


class GHtml(GObj):
    """ GObj that generates html in XML syntax.

    :param fsm: FSM `simple-machine`.
    :param gconfig: GCONFIG `gconfig-template`.

    .. ginsfsm::
       :fsm: GHTML_FSM
       :gconfig: GHTML_GCONFIG


    """
    def __init__(self, fsm=None, gconfig=None):
        gconfig = add_gconfig(gconfig, GHTML_GCONFIG)
        if fsm is None:
            fsm = {}
        super(GHtml, self).__init__(fsm, gconfig)

    def start_up(self):
        """ Initialization zone.
        """

    def add_extra_template(self, template):
        """ Add a template to the extra_template
        """
        extra_template = self.read_parameter('extra_template')
        extra_template += template
        self.write_parameters(extra_template=extra_template)

    def _write_attribs(self, buf):
        for key, value in iteritems_(self.config.attrib):
            buf.write(' %s="%s"' % (key, value))

    def _render_template(self, buf, mako_lookup, **kw):
        # TopLevelNotFound
        # render main template
        ctx = Context(buf, **kw)
        template = None
        if mako_lookup:
            try:
                template = mako_lookup.get_template(self.config.template)
            except TopLevelLookupException:
                pass

        if not template:
            if self.config.template:
                template = Template(
                    self.config.template,
                    strict_undefined=True,
                )
        if template:
            template.render_context(ctx)

        # render extra template
        template = None
        if self.config.extra_template:
            if mako_lookup:
                try:
                    # TODO: this is slow if it's not a file! optimize
                    template = mako_lookup.get_template(self.config.extra_template)
                except TopLevelLookupException:
                    pass
            if not template:
                template = Template(
                    self.config.extra_template,
                    strict_undefined=True,
                )
        if template:
            template.render_context(ctx)

    def render(self, buf=None, mako_lookup=None, **kw):
        kw.update({'this': self})
        buf_is_mine = False
        if buf is None:
            buf = NativeIO()
            buf_is_mine = True

        if self.config.tag:
            buf.write('<%s' % self.config.tag)
            self._write_attribs(buf)
            buf.write('>')

            if not self.config.tag in void_elements:
                # by the moment, the order is: self.config.text, template, childs
                if self.config.text:
                    buf.write(self.config.text)
                if self.config.template:
                    self._render_template(
                        buf,
                        mako_lookup,
                        **kw
                    )
                for child in self:
                    child.render(buf=buf, mako_lookup=mako_lookup, **kw)
            buf.write('</%s>' % self.config.tag)

        elif self.config.template:
            # the gobj name is the mako variable of parent template,
            # where insert the child rendered template.
            childs_buf = NativeIO()
            child_templates = {}
            for child in self:
                if not child.name:
                    raise Exception('You must use named gobjs %r' % child)
                child.render(buf=childs_buf, mako_lookup=mako_lookup, **kw)
                s = childs_buf.getvalue()
                rendered_child = tostr(s)
                child_templates[child.name] = rendered_child
                childs_buf.truncate(0)

            childs_buf.close()
            kw.update(child_templates)
            self._render_template(buf, mako_lookup, **kw)

        s = buf.getvalue()
        s = tostr(s)
        if buf_is_mine:
            buf.close()
        return s
