"""Comment notification hooks

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb import RegistryException
from cubicweb.predicates import is_instance
from cubicweb.sobjects import notification


class CommentAddedView(notification.NotificationView):
    """get notified from new comments"""
    __regid__ = 'notif_after_add_relation_comments'
    __select__ = is_instance('Comment',)
    msgid_timestamp = False

    def subject(self):
        root = self.cw_rset.get_entity(self.cw_row, self.cw_col).cw_adapt_to('ITree').root()
        return '%s %s %s' % (self._cw._('new comment for'),
                             root.dc_type(),
                             root.dc_title())

    def cell_call(self, row, col=0, **kwargs):
        self.cw_row, self.cw_col = row, col
        try:
            view = self._cw.vreg['views'].select('fullthreadtext', self._cw,
                                             rset=self.cw_rset, row=row, col=col)
        except RegistryException:
            return
        return view.render(row=row, col=col, w=self.w, **kwargs)
