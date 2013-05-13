# -*- encoding: utf-8 -*-
from ghtml.c_ghtml import GHtml


class Boxlist(GHtml):
    def __init__(self, fsm=None, gconfig=None):
        super(Boxlist, self).__init__(fsm=fsm, gconfig=gconfig)

    def start_up(self):
        """  Create childs here
        """

    def render(self, **kw):
        return super(Boxlist, self).render(**kw)


def create_boxlist(name, parent, **kw):
    boxlist = parent.create_gobj(
        name,
        Boxlist,
        parent,
        template='/%s/htmlrendercode/widgets/boxlist/boxlist.mako' % (
            __package__.split('.')[0]),
        **kw
    )
    return boxlist
