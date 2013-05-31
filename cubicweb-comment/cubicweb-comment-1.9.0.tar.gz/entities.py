"""entity classes for Comment entities

:organization: Logilab
:copyright: 2003-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.common.textutils import normalize_text
from rql import TypeResolverException

from cubicweb import uilib
from cubicweb.view import EntityView
from cubicweb.predicates import is_instance
from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.entities.adapters import ITreeAdapter

def subcomments_count(commentable):
    return sum([len(commentable.reverse_comments)]
               + [subcomments_count(c) for c in commentable.reverse_comments])

class Comment(AnyEntity):
    """customized class for Comment entities"""
    __regid__ = 'Comment'
    fetch_attrs, cw_fetch_order = fetch_config(('creation_date',),
                                               'creation_date', order='ASC')

    def dc_title(self):
        return uilib.cut(self.printable_value('content', format='text/plain'), 50)

    def dc_description(self, format='text/plain'):
        return self.printable_value('content', format=format)

    subcomments_count = subcomments_count


class CommentITreeAdapter(ITreeAdapter):
    __select__ = is_instance('Comment')
    tree_relation = 'comments'


# some views potentially needed on web *and* server side (for notification)
# so put them here

class CommentFullTextView(EntityView):
    __regid__ = 'fulltext'
    __select__ = is_instance('Comment')

    def cell_call(self, row, col, indentlevel=0, withauthor=True):
        e = self.cw_rset.get_entity(row,col)
        if indentlevel:
            indentstr = '>'*indentlevel + ' '
        else:
            indentstr = ''
        if withauthor:
            _ = self._cw._
            author = e.created_by and e.created_by[0].login or _("Unknown author")
            head = u'%s%s - %s :' % (indentstr,
                                     _('On %s') %  self._cw.format_date(e.creation_date, time=True),
                                     _('%s wrote') % author)
            lines = [head]
        else:
            lines = []
        content = e.printable_value('content', format='text/plain')
        lines.append(normalize_text(content, 80, indentstr,
                                    rest=e.content_format=='text/rest'))
        lines.append(indentstr[:-2])
        self.w(u'\n'.join(lines))


class CommentFullThreadText(CommentFullTextView):
    """display a comment and its parents"""
    __regid__ = 'fullthreadtext'

    def cell_call(self, row, col):
        e = self.cw_rset.get_entity(row,col)
        strings = []
        itree = e.cw_adapt_to('ITree')
        cpath = itree.path()[1:]
        indentlevel = len(cpath) - 1
        for i, ceid in enumerate(cpath):
            try:
                comment = self._cw.execute('Any C,T,D WHERE C creation_date D, C content T, C eid %(x)s',
                                           {'x': ceid}, build_descr=True).get_entity(0, 0)
            except TypeResolverException:
                # not a comment
                continue
            strings.append(comment.view('fulltext', indentlevel=indentlevel-i,
                                        withauthor=i!=indentlevel).strip() + '\n')
        strings.append(u'\n%s: %s' % (self._cw._('i18n_by_author_field'),
                                      e.dc_creator() or _('unknown author')))
        strings.append(u'url: %s' % itree.root().absolute_url())
        self.w(u'\n'.join(strings))


class CommentFullThreadDescText(CommentFullTextView):
    """same as fullthreadtext, but going from top level object to leaf comments
    """
    __regid__ = 'fullthreadtext_descending'

    def cell_call(self, row, col, indentlevel=0):
        e = self.cw_rset.get_entity(row,col)
        self.w(e.view('fulltext', indentlevel=indentlevel).strip() + '\n')
        subcommentsrset = e.related('comments', 'object')
        if subcommentsrset:
            self.wview('fulltext', subcommentsrset, indentlevel=indentlevel+1)
