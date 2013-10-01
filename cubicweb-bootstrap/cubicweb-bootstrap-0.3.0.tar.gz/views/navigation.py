# -*- coding: utf-8 -*-
"""bootstrap implementation of navigation components

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from logilab.common.decorators import monkeypatch

from logilab.mtconverter import xml_escape

from cubicweb.web.component import NavigationComponent

from cubicweb.web.views.navigation import (NextPrevNavigationComponent,
                                           SortedNavigation,
                                           PageNavigation,
                                           PageNavigationSelect)

NavigationComponent.page_link_templ = u'<li><a href="%s" title="%s">%s</a></li>'
NavigationComponent.selected_page_link_templ = u'<li class="active"><a href="%s" title="%s">%s</a></li>'
NavigationComponent.previous_page_link_templ = NavigationComponent.next_page_link_templ = NavigationComponent.page_link_templ
NavigationComponent.no_previous_page_link = u'<li class="disabled"><a href="#">«</a></li>'
NavigationComponent.no_next_page_link = u'<li class="disabled"><a href="#">»</a></li>'
NavigationComponent.no_content_prev_link = u'«'
NavigationComponent.no_content_next_link = u'»'


@monkeypatch(SortedNavigation)
def write_links(self, basepath, params, blocklist):
    """Return HTML for the whole navigation: `blocklist` is a list of HTML
    snippets for each page, `basepath` and `params` will be necessary to
    build previous/next links.
    """
    self.w(u'<ul class="pagination">')
    self.w(u'%s&#160;' % self.previous_link(basepath, params))
    self.w(u'%s' % u''.join(blocklist))
    self.w(u'&#160;%s' % self.next_link(basepath, params))
    self.w(u'</ul>')


@monkeypatch(PageNavigation)
def call(self):
    """displays a resultset by page"""
    params = dict(self._cw.form)
    self.clean_params(params)
    basepath = self._cw.relative_path(includeparams=False)
    self.w(u'<ul class="pagination">')
    self.w(u'%s&#160;' % self.previous_link(basepath, params))
    self.w(u'&#160;'.join(self.iter_page_links(basepath, params)))
    self.w(u'&#160;%s' % self.next_link(basepath, params))
    self.w(u'</ul>')


NextPrevNavigationComponent.prev_icon = u'&#8592;'
NextPrevNavigationComponent.next_icon = u'&#8594;'

@monkeypatch(NextPrevNavigationComponent)
# Should be better done, but this works
def render_body(self, w):
    w(u'<div class="prevnext row">')
    w(u'<ul class="pager">')
    self.prevnext(w)
    w(u'</ul>')
    w(u'</div>')
    #w(u'<div class="clear"></div>')

@monkeypatch(NextPrevNavigationComponent)
def prevnext_div(self, w, type, cssclass, url, title, content):
    cssclass = u'col-md-6'

    w(u'<li class="%s">' % cssclass)
    w(u'<a href="%s" title="%s">%s</a>' % (xml_escape(url),
                                           xml_escape(title),
                                           content))
    w(u'</li>')
    self._cw.html_headers.add_raw('<link rel="%s" href="%s" />' % (
          type, xml_escape(url)))


def do_paginate(view, rset=None, w=None, show_all_option=True, page_size=None):
    """write pages index in w stream (default to view.w) and then limit the
    result set (default to view.rset) to the currently displayed page if we're
    not explicitly told to display everything (by setting __force_display in
    req.form)
    """
    req = view._cw
    if rset is None:
        rset = view.cw_rset
    if w is None:
        w = view.w
    nav = req.vreg['components'].select_or_none(
        'navigation', req, rset=rset, page_size=page_size, view=view)
    if nav:
        if w is None:
            w = view.w
        if req.form.get('__force_display'):
            # allow to come back to the paginated view
            params = dict(req.form)
            basepath = req.relative_path(includeparams=False)
            del params['__force_display']
            url = nav.page_url(basepath, params)
            w(u'<div class="displayAllLink">'
              u'<a href="%s">%s</a></div>\n'
              % (xml_escape(url), req._('back to pagination (%s results)')
                                  % nav.page_size))
        else:
            # get boundaries before component rendering
            start, stop = nav.page_boundaries()
            nav.render(w=w)
            params = dict(req.form)
            nav.clean_params(params)
            # make a link to see them all
            if show_all_option:
                basepath = req.relative_path(includeparams=False)
                params['__force_display'] = 1
                params['__fromnavigation'] = 1
                url = nav.page_url(basepath, params)
                w(u'<div class="displayAllLink">'
                  u'<a href="%s">%s</a></div>\n'
                  % (xml_escape(url), req._('show %s results') % len(rset)))
            rset.limit(offset=start, limit=stop-start, inplace=True)


def paginate(view, show_all_option=True, w=None, page_size=None, rset=None):
    """paginate results if the view is paginable
    """
    if view.paginable:
        do_paginate(view, rset, w, show_all_option, page_size)

# monkey patch base View class to add a .paginate([...])
# method to be called to write pages index in the view and then limit the result
# set to the current page
from cubicweb.view import View
View.do_paginate = do_paginate
View.paginate = paginate
View.handle_pagination = False

@monkeypatch(PageNavigationSelect)
def call(self):
    params = dict(self._cw.form)
    self.clean_params(params)
    basepath = self._cw.relative_path(includeparams=False)
    w = self.w
    w(u'<ul class="pagination">')
    w(self.previous_link(basepath, params))
    w(u'<li><select onchange="javascript: document.location=this.options[this.selectedIndex].value">')
    for option in self.iter_page_links(basepath, params):
        w(option)
    w(u'</select></li>')
    w(u'&#160;%s' % self.next_link(basepath, params))
    w(u'</ul>')

PageNavigationSelect.page_link_templ = u'<option value="%s" title="%s">%s</option>'
PageNavigationSelect.selected_page_link_templ = u'<option value="%s" selected="selected" title="%s">%s</option>'
