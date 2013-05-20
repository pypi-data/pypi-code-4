# -*- encoding: utf-8 -*-
from ghtml.c_ghtml import GHtml
from ginsfsm.gconfig import add_gconfig

CONTENT_GCONFIG = {
    'gaplic_namespace': [
        str, '', 0, None,
        'namespace of gaplic, to store callbacks.',
    ],
}


class Content(GHtml):
    def __init__(self, fsm=None, gconfig=None):
        gconfig = add_gconfig(gconfig, CONTENT_GCONFIG)
        super(Content, self).__init__(fsm=fsm, gconfig=gconfig)

    def start_up(self):
        """  Create childs here
        """
        from widgets.boxlist.boxlist import create_boxlist
        create_boxlist(
            'boxlist',
            self,
        )

    def render(self, **kw):
        return super(Content, self).render(**kw)


def create_content(name, parent, **kw):
    content = parent.create_gobj(
        name,
        Content,
        parent,
        template='/%s/htmlrendercode/content.mako' % (
            __package__.split('.')[0]),
        **kw
    )
    return content
