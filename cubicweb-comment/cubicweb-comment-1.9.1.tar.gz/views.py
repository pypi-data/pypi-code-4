"""Specific views and actions for application using the Comment entity type

:organization: Logilab
:copyright: 2003-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
from __future__ import with_statement

__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import xml_escape

from cubicweb.predicates import (is_instance, has_permission, authenticated_user,
                                 score_entity, relation_possible, one_line_rset,
                                 match_kwargs, match_form_params,
                                 partial_relation_possible)
from cubicweb.view import EntityView
from cubicweb.uilib import cut, js
from cubicweb.web import uicfg, component, form, formwidgets as fw
from cubicweb.web.action import LinkToEntityAction, Action
from cubicweb.web.views import primary, baseviews, xmlrss, treeview, ajaxedit

_afs = uicfg.autoform_section
_afs.tag_object_of(('*', 'comments', '*'), formtype='main', section='hidden')

_affk = uicfg.autoform_field_kwargs
_affk.tag_subject_of(('*', 'comments', '*'), {'widget': fw.HiddenInput})

_abaa = uicfg.actionbox_appearsin_addmenu
_abaa.tag_subject_of(('*', 'comments', '*'),  False)
_abaa.tag_object_of(('*', 'comments', '*'), False)

_pvs = uicfg.primaryview_section
_pvs.tag_subject_of(('*', 'comments', '*'),  'hidden')
_pvs.tag_object_of(('*', 'comments', '*'), 'hidden')


# comment views ###############################################################

class CommentPrimaryView(primary.PrimaryView):
    __select__ = is_instance('Comment')

    def cell_call(self, row, col):
        self._cw.add_css('cubes.comment.css')
        entity = self.cw_rset.complete_entity(row, col)
        # display text, author and creation date
        self.w(u'<div class="comment">')
        self.w(u'<div class="commentInfo">')
        # do not try to display creator when you're not allowed to see CWUsers
        if entity.creator:
            authorlink = entity.creator.view('oneline')
            self.w(u'%s %s\n' % (self._cw._('written by'), authorlink))
        self.w(self._cw.format_date(entity.creation_date))
        # commented object
        if entity.comments:
            self.w(u",  %s " % self._cw._('comments'))
            entity.comments[0].view('oneline', w=self.w)
            self.w(u"\n")
        # don't include responses in this view, since the comment section
        # component will display them
        self.w(u'</div>\n')
        self.w(u'<div class="commentBody">%s</div>\n'
               % entity.printable_value('content'))
        # XXX attribute generated_by added by email component
        if hasattr(entity, 'generated_by') and entity.generated_by:
            gen = entity.generated_by[0]
            link = '<a href="%s">%s</a>' % (gen.absolute_url(),
                                            gen.dc_type().lower())
            txt = self._cw._('this comment has been generated from this %s') % link
            self.w(u'<div class="commentBottom">%s</div>\n' % txt)
        self.w(u'</div>\n')


class CommentRootView(EntityView):
    __regid__ = 'commentroot'
    __select__ = is_instance('Comment')

    def cell_call(self, row, col, **kwargs):
        entity = self.cw_rset.get_entity(row, col)
        root = entity.cw_adapt_to('ITree').root()
        self.w(u'<a href="%s">%s %s</a> ' % (
            xml_escape(root.absolute_url()),
            xml_escape(root.dc_type()),
            xml_escape(cut(root.dc_title(), 40))))


class CommentSummary(EntityView):
    __regid__ = 'commentsummary'
    __select__ = is_instance('Comment')

    def cell_call(self, row, col, **kwargs):
        entity = self.cw_rset.get_entity(row, col)
        maxsize = self._cw.property_value('navigation.short-line-size')
        content = entity.printable_value('content', format='text/plain')
        self.w(xml_escape(cut(content, maxsize)))


class CommentOneLineView(baseviews.OneLineView):
    __select__ = is_instance('Comment')

    def cell_call(self, row, col, **kwargs):
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'[%s] ' % entity.view('commentroot'))
        self.w(u'<a href="%s"><i>%s</i></a>\n' % (
            xml_escape(entity.absolute_url()),
            entity.view('commentsummary')))


class CommentTreeItemView(baseviews.ListItemView):
    __regid__ = 'treeitem'
    __select__ = is_instance('Comment')

    def cell_call(self, row, col, **kwargs):
        self._cw.add_js('cubicweb.ajax.js')
        self._cw.add_css('cubes.comment.css')
        entity = self.cw_rset.get_entity(row, col)
        actions = self._cw.vreg['actions']
        # DOM id of the whole comment's content
        cdivid = 'comment%sDiv' % entity.eid
        self.w(u'<div id="%s">' % cdivid)
        self.w(u'<div class="commentInfo">')
        self.w(self._cw.format_date(entity.creation_date))
        self.w(u' %s' % self._cw.format_time(entity.creation_date))
        if entity.creator:
            authorlink = entity.creator.view('oneline')
            self.w(u', %s <span class="author">%s</span> \n'
                   % (self._cw._('written by'), authorlink,))
        replyaction = actions.select_or_none('reply_comment', self._cw,
                                       rset=self.cw_rset, row=row)
        if replyaction is not None:
            url = self._cw.ajax_replace_url('comment%sHolder' % entity.eid,
                                            eid=entity.eid, vid='addcommentform')
            self.w(u' | <span class="replyto"><a href="%s">%s</a></span>'
                   % (xml_escape(url), self._cw._(replyaction.title)))
        editaction = actions.select_or_none('edit_comment', self._cw,
                                            rset=self.cw_rset, row=row)
        if editaction is not None:
            # split(':', 1)[1] to remove javascript:
            formjs = self._cw.ajax_replace_url(
                cdivid, 'append', eid=entity.eid,
                vid='editcommentform').split(':', 1)[1]
            url = "javascript: jQuery('#%s div').hide(); %s" % (cdivid, formjs)
            self.w(u' | <span class="replyto"><a href="%s">%s</a></span>'
                   % (xml_escape(url), self._cw._(editaction.title)))

        deleteaction = actions.select_or_none('delete_comment', self._cw,
                                             rset=self.cw_rset, row=row)
        if deleteaction is not None:
            root = entity.cw_adapt_to('ITree').root()
            url = self._cw.ajax_replace_url(
                'comment%s' % entity.eid, eid=entity.eid, vid='deleteconf',
                __redirectpath=root.rest_path())

            self.w(u' | <span class="replyto"><a href="%s">%s</a></span>'
                   % (xml_escape(url), self._cw._(deleteaction.title)))
        self.w(u'</div>\n') # close comment's info div
        self.w(u'<div class="commentBody">%s</div>\n'
               % entity.printable_value('content'))
        # holder for reply form
        self.w(u'<div id="comment%sHolder" class="replyComment"></div>' % entity.eid)
        self.w(u'</div>\n') # close comment's content div


class CommentThreadView(treeview.BaseTreeView):
    """a recursive tree view"""
    __select__ = is_instance('Comment')
    title = _('thread view')

    def open_item(self, entity):
        self.w(u'<li id="comment%s" class="comment">\n' % entity.eid)


class RssItemCommentView(xmlrss.RSSItemView):
    __select__ = is_instance('Comment')

    def cell_call(self, row, col):
        entity = self.cw_rset.complete_entity(row, col)
        self.w(u'<item>\n')
        self.w(u'<guid isPermaLink="true">%s</guid>\n'
               % xml_escape(entity.absolute_url()))
        self.render_title_link(entity)
        root = entity.cw_adapt_to('ITree').root()
        description = entity.dc_description(format='text/html') + \
                      self._cw._(u'about') + \
                      u' <a href=%s>%s</a>' % (root.absolute_url(),
                                               root.dc_title())
        self._marker('description', description)
        self._marker('dc:date', entity.dc_date(self.date_format))
        self.render_entity_creator(entity)
        self.w(u'</item>\n')
        self.wview('rssitem', entity.related('comments', 'object'), 'null')


# comment forms ################################################################

class InlineEditCommentFormView(form.FormViewMixIn, EntityView):
    __regid__ = 'editcommentform'
    __select__ = is_instance('Comment')

    def entity_call(self, entity):
        self.comment_form(entity)

    def propose_to_login(self):
        self.w(u'<div class="warning">%s ' % self._cw._('You are not authenticated. Your comment will be anonymous if you do not <a onclick="showLoginBox()">login</a>.'))
        if 'registration' in self._cw.vreg.config.cubes():
            self.w(self._cw._(u' If you have no account, you may want to <a href="%s">create one</a>.')
                   % self._cw.build_url('register'))
        self.w(u'</div>')

    def comment_form(self, commented, newcomment=None):
        self._cw.add_js(('cubicweb.edition.js', 'cubes.comment.js'))
        if self._cw.cnx.anonymous_connection:
            self.propose_to_login()
        entity = newcomment or commented
        okjs = js.processComment(commented.eid, not entity.has_eid(),
                                 not (newcomment is None or commented.has_eid()),
                                 self.cw_extra_kwargs.get('context'))
        canceljs = js.cancelCommentEdition(commented.eid, not entity.has_eid())
        form, formvalues = ajaxedit.ajax_composite_form(
            commented, newcomment, 'comments', okjs, canceljs)
        self.w(u'<div id="comment%sSlot">' % commented.eid)
        form.render(w=self.w, formvalues=formvalues,
                    main_form_title=u'', display_label=False)
        self.w(u'</div>')


class InlineAddCommentFormView(InlineEditCommentFormView):
    __regid__ = 'addcommentform'
    __select__ = (relation_possible('comments', 'object', 'Comment', 'add')
                  | match_form_params('etype'))

    def call(self, **kwargs):
        if self.cw_rset is None:
            entity = self._cw.vreg['etypes'].etype_class(self._cw.form['etype'])(self._cw)
            entity.eid = self._cw.form['tempEid']
            self.entity_call(entity)
        else:
            super(InlineAddCommentFormView, self).call(**kwargs)

    def entity_call(self, commented):
        newcomment = self._cw.vreg['etypes'].etype_class('Comment')(self._cw)
        newcomment.eid = self._cw.varmaker.next()
        self.comment_form(commented, newcomment)


# contextual components ########################################################

class CommentSectionVComponent(component.EntityCtxComponent):
    """a component to display a <div> html section including comments
    related to an object
    """
    __regid__ = 'commentsection'
    __select__ = (component.EntityCtxComponent.__select__
                  & relation_possible('comments', 'object', 'Comment'))

    context = 'navcontentbottom'

    def render_body(self, w):
        req = self._cw
        req.add_js( ('cubicweb.ajax.js', 'cubes.comment.js') )
        entity = self.entity
        addcomment = self._cw.vreg['actions'].select_or_none(
            'reply_comment', req, entity=entity,
            rset=entity.cw_rset, row=entity.cw_row, col=entity.cw_col)
        if entity.has_eid():
            rql = u'Any C,CD,CC,CCF,U,UL,US,UF ORDERBY CD WHERE C is Comment, '\
                  'C comments X, C creation_date CD, C content CC, C content_format CCF, ' \
                  'C created_by U?, U login UL, U firstname UF, U surname US, X eid %(x)s'
            rset = req.execute(rql, {'x': entity.eid})
            if rset.rowcount:
                w(u'<h4>%s</h4>' % (req._('Comment_plural')))
                w(u'<ul class="comment">')
                for i in xrange(rset.rowcount):
                    self._cw.view('tree', rset, row=i, w=w)
                w(u'</ul>')
        if addcomment is not None:
            url = self.lazy_view_holder(w, entity, 'addcommentform')
            w(u' <span class="addcomment">(<a href="%s">%s</a>)</span>' % (xml_escape(url), req._(addcomment.title)))


class UserLatestCommentsSection(component.EntityCtxComponent):
    """a section to display latest comments by a user"""
    __select__ = component.EntityCtxComponent.__select__ & is_instance('CWUser')
    __regid__ = 'latestcomments'
    context = 'navcontentbottom'

    def render_body(self, w):
        maxrelated = self._cw.property_value('navigation.related-limit') + 1
        rset = self._cw.execute(
            'Any C,CD,C,CCF ORDERBY CD DESC LIMIT %s WHERE C is Comment, '
            'C creation_date CD, C content CC, C content_format CCF, '
            'C created_by U, U eid %%(u)s' % maxrelated,
            {'u': self.entity.eid})
        if rset:
            w(u'<div class="section">')
            w(u'<h4>%s</h4>\n' % self._cw._('Latest comments').capitalize())
            self._cw.view('table', rset, w=w,
                          headers=[_('about'), _('on date'),
                                   _('comment content')],
                      cellvids={0: 'commentroot',
                                2: 'commentsummary',
                                })
            w(u'</div>')

# adapters #####################################################################

# XXX implements ibreadcrumbs instead
from cubicweb.web.views.editcontroller import IEditControlAdapter

class CommentIEditControlAdapter(IEditControlAdapter):
    __select__ = is_instance('Comment')

    def after_deletion_path(self):
        """return (path, parameters) which should be used as redirect
        information when this entity is being deleted
        """
        return self.entity.cw_adapt_to('ITree').root().rest_path(), {}

# actions ######################################################################

class ReplyCommentAction(LinkToEntityAction):
    __regid__ = 'reply_comment'
    __select__ = LinkToEntityAction.__select__ & is_instance('Comment')

    rtype = 'comments'
    role = 'object'
    target_etype = 'Comment'

    title = _('reply to this comment')
    category = 'hidden'
    order = 111

    def url(self):
        comment = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        linkto = '%s:%s:subject' % (self.rtype, comment.eid)
        root = comment.cw_adapt_to('ITree').root()
        return self._cw.build_url(vid='creation', etype=self.target_etype,
                                  __linkto=linkto,
                                  __redirectpath=root.rest_path(),
                                  __redirectvid=self._cw.form.get('vid', ''))


class AddCommentAction(LinkToEntityAction):
    """add comment is like reply for everything but Comment"""
    __regid__ = 'reply_comment'
    __select__ = ((LinkToEntityAction.__select__
                   | (match_kwargs('entity') & partial_relation_possible(action='add', strict=True)))
                   & ~is_instance('Comment'))

    rtype = 'comments'
    role = 'object'
    target_etype = 'Comment'

    title = _('add comment')
    category = 'hidden'
    order = 111


class EditCommentAction(Action):
    __regid__ = 'edit_comment'
    __select__ = one_line_rset() & is_instance('Comment') & has_permission('update')

    title = 'modify' # not internationalized on purpose (wanna use cw translation)
    category = 'hidden'
    order = 110

    def url(self):
        return self._cw.build_url(rql=self.cw_rset.printable_rql(), vid='edition')

class DeleteCommentAction(Action):
    __regid__ = 'delete_comment'
    __select__ = is_instance('Comment') & authenticated_user() & \
                 score_entity(lambda x: not x.reverse_comments and x.cw_has_perm('delete'))

    title = 'delete' # not internationalized on purpose (wanna use cw translation)
    category = 'hidden'
    order = 110

    def url(self):
        return self._cw.build_url(rql=self.cw_rset.printable_rql(), vid='deleteconf')
