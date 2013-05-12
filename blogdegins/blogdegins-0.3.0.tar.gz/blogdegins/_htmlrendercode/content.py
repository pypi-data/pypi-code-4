# -*- encoding: utf-8 -*-
from ghtml.c_ghtml import GHtml


class Content(GHtml):
    def __init__(self, fsm=None, gconfig=None):
        super(Content, self).__init__(fsm=fsm, gconfig=gconfig)

    def start_up(self):
        """  Create more childs here
        create_datalayout(
            'datalayout',
            self,
            gaplic_namespace=self.config.gaplic_namespace
        )
        """

    def render(self, **kw):
        return super(Content, self).render(**kw)


def create_content(name, parent, **kw):
    content = parent.create_gobj(
        name,
        Content,
        parent,
        template='/%s/htmlrendercode/content.mako' % (
            __package__.rpartition('.')[0]),
        **kw
    )
    return content
