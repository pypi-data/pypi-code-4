"""gingouz specific boxes

:organization: Logilab
:copyright: 2003-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from datetime import date

from logilab.common.date import first_day
from logilab.common.registry import objectify_predicate
from logilab.mtconverter import xml_escape

from cubicweb import tags
from cubicweb.web import component

@objectify_predicate
def has_resource(cls, req, **kwargs):
    return bool(req.user.cw_adapt_to('timesheet.IResource'))


class ActivitiesBox(component.CtxComponent):
    """display a box with an activity calendar"""
    __regid__ = 'timesheet.activities_box'
    __select__ = component.CtxComponent.__select__ & has_resource()
    visible = True # enabled by default
    title = _('My activities')
    order = 10

    def render_title(self, w):
        title = self._cw._(self.title)
        url = self._cw.build_url(rql="Any C WHERE R use_calendar CU, CU use_calendar C, "
                                 "R euser U, U eid %s" % self._cw.user.eid)
        title += u'&nbsp;&nbsp;<a href="%s" title="%s"><img alt="calendar icon" src="%s"/> </a>' % (
            xml_escape(url), self._cw._('see my calendars'),
            xml_escape(self._cw.data_url('office-calendar.png')))
        w(title)

    def render_body(self, w):
        resource = self._cw.user.cw_adapt_to('timesheet.IResource').resource
        resource.view('activity_calendar', firstday=first_day(date.today()),
                      calid='selftid', w=w)


class MyActionsBox(component.CtxComponent):
    """display a box with util links"""
    __regid__ = 'timesheet.my_actions_box'
    __select__ = component.CtxComponent.__select__ & has_resource()

    visible = True # enabled by default
    title = _('My actions')
    order = 3

    def render_body(self, w):
        req = self._cw
        resource = req.user.cw_adapt_to('timesheet.IResource').resource
        self.append(tags.a(req._('my_space'), href=resource.absolute_url()))
        # select default calendar for currently logged user
        if resource.default_calendar:
            cal = resource.default_calendar
            action = req.vreg['actions'].select('ask-off-days', req,
                                                rset=cal.as_rset())
            self.append(tags.a(req._(action.title), href=action.url()))
        self.render_items(w)
