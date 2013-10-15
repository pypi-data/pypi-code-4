# -*- coding: utf-8 -*-
"""activity related views.

:organization: Logilab
:copyright: 2007-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

import datetime

from logilab.common.date import todate

from logilab.mtconverter import xml_escape

from cubicweb.utils import UStringIO
from cubicweb.schema import display_name
from cubicweb.predicates import (is_instance, empty_rset, multi_columns_rset,
                                match_user_groups, score_entity)
from cubicweb.view import AnyRsetView, EntityView, EntityAdapter
from cubicweb.web import INTERNAL_FIELD_VALUE, stdmsgs, action
from cubicweb.web.views import tableview, calendar, navigation, editcontroller

from cubes.calendar.views import get_date_range_from_reqform

class ActivitySummaryView(AnyRsetView):
    __regid__ = 'actsummary'
    __select__ = is_instance('Activity') & multi_columns_rset(7)

    # XXX we should make a very strict selector here
    def call(self):
        total_duration = sum(e.duration for e in self.cw_rset.entities())
        self.w(u'<h3>%s: %s</h3>' % (_('total'), total_duration))
        self.wview('table', self.cw_rset, 'null', displaycols=range(1,6))

        resdict = {}
        for __, __, res, __, duration, __, login in self.cw_rset:
            resdur = resdict.get(login, 0)
            resdur += duration
            resdict[login] = resdur
        self.w(u'<h2>%s</h2>' % _('statistics'))
        self.w(u'<table class="listing">')
        self.w(u'<tr><th>%s</th><th>%s</th></tr>' % (_('resource'), _('duration')))
        for even_odd, (login, resdur) in enumerate(sorted(resdict.iteritems())):
            self.w(u'<tr class="%s">' % (even_odd % 2 and "odd" or "even"))
            self.w(u'<td>%s</td>' % login)
            self.w(u'<td>%s</td>' % resdur)
            self.w(u'</tr>')
        self.w(u'</table>')

class ActivitySubmitView(EntityView):
    __regid__ = 'activities-list'
    __select__ = is_instance('Resource')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        firstday, lastday = get_date_range_from_reqform(self._cw.form)
        rql = 'Any A WHERE A is Activity, A done_by R, R eid %(r)s'
        if lastday is None:
            rql += ', A diem %(fd)s'
        else:
            rql += ', A diem >= %(fd)s, A diem <= %(ld)s'
        rset = self._cw.execute(rql, {'r': entity.eid,
                                      'fd': firstday, 'ld': lastday})
        self.wview('activitytable', rset, 'null')
        self.wview('activities-submitform',
                   rset=self.cw_rset, row=row, col=col,
                   initargs={'date': firstday})


# XXX see generic definition for tablecontext view in gingouz.views
class ActivityTableContext(EntityView):
    __regid__ = 'tablecontext'
    __select__ = is_instance('Activity')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'<a href="%s"><img alt="%s" src="data/accessories-text-editor.png" /></a>' %
               (xml_escape(entity.absolute_url(vid='edition')),
                self._cw._('actions_edit')))


class ActivityTable(EntityView):
    __regid__ = 'activitytable'
    __select__ = is_instance('Activity')
    title = _('activitytable')

    def call(self, showresource=True):
        _ = self._cw._
        headers  = [_("diem"), _("duration"), _("workpackage"), _("description"), _("state"), u""]
        eids = ','.join(str(row[0]) for row in self.cw_rset)
        rql = ('Any R, D, DUR, WO, DESCR, S, A, SN, RT, WT ORDERBY D DESC '
               'WHERE '
               '   A is Activity, A done_by R, R title RT, '
               '   A diem D, A duration DUR, '
               '   A done_for WO, WO title WT, '
               '   A description DESCR, A in_state S, S name SN, A eid IN (%s)' % eids)
        if showresource:
            displaycols = range(7)
            headers.insert(0, display_name(self._cw, 'Resource'))
        else: # skip resource column if asked to
            displaycols = range(1, 7)
        rset = self._cw.execute(rql)
        self.wview('editable-table', rset, 'null', #subvid='tablecontext',
                   displayfilter=True, displayactions=False,
                   headers=headers, displaycols=displaycols,
                   cellvids={3: 'editable-final'})


class GenericActivityTable(tableview.EditableTableView):
    __regid__ = 'generic-activitytable'
    __select__ = multi_columns_rset()
    title = _('activitytable')

    def call(self, title=None):
        labels = self.columns_labels()
        labels[0] = u'edit'
        strio = UStringIO()
        self.paginate(self, w=strio.write, page_size=20)
        super(GenericActivityTable, self).call(
            #subvid='tablecontext', headers=headers,
            displayfilter=True, displayactions=False, actions=(),
            cellvids={4: 'editable-final'})
        self.w(strio.getvalue())


class ActivityCalendarItemView(calendar.CalendarItemView):
    __select__ = is_instance('Activity')

    def cell_call(self, row, col):
        activity = self.cw_rset.get_entity(row, col)
        self.w(u'<a href="%s">%s %s</a>' % (xml_escape(activity.absolute_url()),
                                            xml_escape(activity.workorder.dc_long_title()),
                                            activity.duration))


class ValidateActivitiesAction(action.Action):
    __regid__ = 'validate-activities'
    __select__ = (action.Action.__select__
                  & match_user_groups('managers')
                  & is_instance('Activity')
                  & score_entity(lambda x: x.cw_adapt_to('IWorkflowable').state == 'pending'))

    category = 'mainactions'
    title = _('validate activities')

    def url(self):
        if self.cw_row is None:
            eids = [row[0] for row in self.cw_rset]
        else:
            eids = (self.cw_rset[self.cw_row][self.cw_col or 0],)
        def validate_cb(req, eids):
            for eid in eids:
                entity = req.entity_from_eid(eid, 'Activity')
                entity.fire_transition('validate')
        msg = self._cw._('activities validated')
        return self._cw.user_callback(validate_cb, (eids,), msg)

WORKORDER_CLOSED_STATES = ('validated', 'canceled')

class MoveActivitiesAction(action.Action):
    __regid__ = 'move-activities'
    __select__ = (action.Action.__select__
                  & match_user_groups('managers')
                  & is_instance('Activity')
                  & score_entity(lambda x: x.cw_adapt_to('IWorkflowable').state == 'pending'))

    category = 'mainactions'
    submenu = _('move activities')

    def actual_actions(self):
        states = ','.join('"%s"' % state for state in WORKORDER_CLOSED_STATES)
        for item in self._cw.execute('Any W,WT,O,OT ORDERBY OT,WT WHERE W is WorkOrder, '
                                     'W in_state S, NOT S name IN (%s), '
                                     'O split_into W, O title OT, W title WT'
                                     % states).entities():
            yield self.build_action(item.dc_long_title(), self.url(item))

    def url(self, workorder):
        if self.cw_row is None:
            eids = [str(row[self.cw_col or 0]) for row in self.cw_rset]
        else:
            eids = [str(self.cw_rset[self.cw_row][self.cw_col or 0])]
        rql = 'SET X done_for Y WHERE X eid IN(%s), Y eid %%(y)s' % ','.join(eids)
        msg = self._cw._('activities moved to workorder %s') % workorder.dc_long_title()
        return self._cw.user_rql_callback((rql, {'y': workorder.eid}), msg)



class ActivityIPrevNextAdapter(navigation.IPrevNextAdapter):
    __select__ = is_instance('Activity')

    def previous_entity(self):
        entity = self.entity
        execute = self._cw.execute
        # if the smallest duration
        rset = execute("Activity A ORDERBY DUR DESC LIMIT 1 WHERE "
                       "A done_by R, R euser U, U eid %(u)s, A diem %(d)s, "
                       "A duration DUR, A duration < %(t)s",
                       {'u': entity.user.eid, 'd': entity.diem,
                        't':entity.duration})
        if rset:
            return rset.get_entity(0, 0)
        # the smallest id
        rset = execute("Activity A ORDERBY A DESC LIMIT 1 WHERE "
                       "A done_by R, R euser U, U eid %(u)s, A diem %(d)s, "
                       "A duration < %(t)s, A eid < %(eid)s",
                       {'u': entity.user.eid, 'd': entity.diem,
                        't': entity.duration, 'eid':entity.eid})
        if rset:
            return rset.get_entity(0, 0)
        # next days
        rset = execute("Activity A ORDERBY D DESC LIMIT 1 WHERE "
                       "A done_by R, R euser U, U eid %(u)s, "
                       "A diem D, A diem < %(d)s ",
                       {'u': entity.user.eid, 'd': entity.diem})
        if rset:
            return rset.get_entity(0, 0)


    def next_entity(self):
        entity = self.entity
        execute = self._cw.execute
        rset = execute("Activity A ORDERBY DUR LIMIT 1 WHERE "
                       "A done_by R, R euser U, U eid %(u)s, A diem %(d)s, "
                       "A duration DUR, A duration > %(t)s",
                       {'u': entity.user.eid, 'd': entity.diem,
                        't': entity.duration})
        if rset:
            return rset.get_entity(0, 0)
        rset = execute("Activity A ORDERBY A LIMIT 1 WHERE "
                       "A done_by R, R euser U, U eid %(u)s, A diem %(d)s, "
                       "A eid > %(eid)s, A duration > %(t)s",
                       {'u': entity.user.eid, 'd': entity.diem,
                        't':entity.duration, 'eid':entity.eid})
        if rset:
            return rset.get_entity(0, 0)
        rset = execute("Activity A ORDERBY D LIMIT 1 WHERE "
                       "A done_by R, R euser U, U eid %(u)s, "
                       "A diem D, A diem > %(d)s ",
                       {'u': entity.user.eid, 'd': entity.diem})
        if rset:
            return rset.get_entity(0, 0)


class ActivityIEditControlAdapter(editcontroller.IEditControlAdapter):
    __select__ = is_instance('Activity')

    def after_deletion_path(self):
        """return (path, parameters) which should be used as redirect
        information when this entity is being deleted
        """
        return 'view', {}


class ActivityICalendarViewsAdapter(EntityAdapter):
    """calendar views interface"""
    __regid__ = 'ICalendarViews'
    __select__ = is_instance('Activity')

    def matching_dates(self, begin, end):
        """calendar views interface"""
        return [self.entity.diem]
