"""gingouz specific primary views
"""

from logilab.mtconverter import xml_escape

from cubicweb.schema import display_name
from cubicweb.view import EntityView
from cubicweb.uilib import toggle_link
from cubicweb.predicates import is_instance, one_line_rset
from cubicweb.web.views import baseviews, primary, tabs

from cubes.calendar.views import primaries as cal_primaries

def print_resource_ratio(self, rset):
    """prints the ratio time spent per resource / time spent by everyone
    """
    if rset:
        duration = sum(duration for r,s,duration,i,di,mi,ma in rset if duration)
        tot_by_res = dict.fromkeys((row[0] for row in rset), 0)
        for r,s,d,i,di,mi,ma in rset:
            tot_by_res[r] += d
        done = set()
        self.w(u'<p>%s</p>' % self._cw._('percentage of time spent per resource'))
        self.w(u'<table class="listing">')
        self.w(u'<tr><th>%s</th><th>%s</th></tr>' % (display_name(self._cw, 'Resource'),
                                                     self._cw._('time spent ratio')))
        for row in xrange(len(rset)):
            if rset[row][0] not in done:
                self.w(u'<tr>')
                entity = rset.get_entity(row, 0)
                eid = entity.eid
                done.add(eid)
                ratio = tot_by_res[eid] * 100 / duration
                self.w(u'<td>%s</td><td>%.2f %%</td>' % (entity.view('oneline'), ratio))
                self.w(u'</tr>')
        self.w(u'</table>')

# order #####################################################################

class OrderPrimaryView(tabs.TabsMixin, primary.PrimaryView):
    __select__ = is_instance('Order') & one_line_rset()
    tabs = [_('activity-overview'), _('activity-details'), _('activity-graph')]
    default_tab = 'activity-overview'

    def render_entity_title(self, entity):
        self.w(u'<h1>%s</h1>' % xml_escape(entity.dc_long_title()))
        if entity.date:
            self.w(u'%s: %s<br />' % (display_name(self._cw, 'date'),
                                      self._cw.format_date(entity.date)))

    def render_entity(self, entity):
        self.render_entity_title(entity)
        rql = 'Any WO ORDERBY T WHERE W eid %(eid)s, W split_into WO, WO title T'
        rset = self._cw.execute(rql, {'eid': entity.eid})
        self.wview('ic_progress_table_view', rset, 'null')
        self.render_tabs(self.tabs, self.default_tab, entity)

class OrderOverviewView(EntityView):
    __regid__ = 'activity-overview'
    __select__ = is_instance('Order')
    title = _('activity-overview')

    def cell_call(self, row, col):
        _ = self._cw._
        entity = self.cw_rset.get_entity(row, col)
        rset = self._cw.execute(entity.rql_activities_groupby_resource, {'eid': entity.eid})
        headers = (_('Resource'), _('status'), _('time spent'), _('begin date'), _('end date'))
        self.wview('table', rset, 'null', headers=headers)
        self.w('<div style="margin-top: 1em"><a href="%s">%s</a></div>' %
               (self._cw.build_url(rql='Any A WHERE A done_for Y, X split_into Y, X eid %s' % entity.eid),
                self._cw._('View all activities')))

class OrderDetailView(EntityView):
    __regid__ = 'activity-details'
    title = _('activity-details')
    __select__ = is_instance('Order') & one_line_rset()

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        rset = self._cw.execute(entity.rql_activities, {'eid': entity.eid})
        self.wview('generic-activitytable', rset, 'null')

class OrderGraphView(EntityView):
    __regid__ = 'activity-graph'
    title = _('activity-graph')
    __select__ = is_instance('Order')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        rql = 'Any D,U WHERE O eid %(eid)s, O split_into W, A done_for W, A diem D, A duration U'
        rset = self._cw.execute(rql, {'eid': entity.eid})
        self.wview('plot', rset, 'null')

# workorder ####################################################################

class WorkorderPrimaryView(tabs.TabsMixin, primary.PrimaryView):
    """display workpackage's activity summary"""
    __select__ = is_instance('WorkOrder') & one_line_rset()
    tabs = [_('activity-overview'), _('activity-details'), _('activity-graph')]
    default_tab = 'activity-overview'

    def render_entity_title(self, entity):
        self.w(u'<h1>%s</h1>' % xml_escape(entity.dc_long_title()))

    def render_entity(self, entity):
        self.render_entity_title(entity)
        view = self._cw.vreg['views'].select('progress_table_view', self._cw,
                                             rset=entity.as_rset())
        columns = list(view.columns)
        for col in ('project', 'milestone'):
            try:
                columns.remove(col)
            except ValueError:
                self.warning('could not remove %s from columns' % col)
        view.render(w=self.w, columns=columns)
        self.render_tabs(self.tabs, self.default_tab, entity)

class WorkOrderOverviewView(EntityView):
    __regid__ = 'activity-overview'
    __select__ = is_instance('WorkOrder')
    title = _('activity-overview')

    def cell_call(self, row, col):
        _ = self._cw._
        entity = self.cw_rset.get_entity(row, col)
        rset = self._cw.execute(entity.rql_activities_groupby_resource, {'eid': entity.eid})
        headers = (_('Resource'), _('status'), _('time spent'), _('begin date'), _('end date'))
        self.wview('table', rset, 'null', headers=headers)
        self.w('<div style="margin-top: 1em"><a href="%s">%s</a></div>' %
               (self._cw.build_url(rql='Any A WHERE A done_for X, X eid %s' % entity.eid),
                self._cw._('view all activities')))


class WorkOrderDetailView(EntityView):
    __regid__ = 'activity-details'
    __select__ = is_instance('WorkOrder') & one_line_rset()
    title = _('activity-details')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        rset = self._cw.execute(entity.rql_activities, {'eid': entity.eid})
        self.wview('generic-activitytable', rset, 'null')

class WorkOrderGraphView(EntityView):
    __regid__ = 'activity-graph'
    title = _('activity-graph')
    __select__ = is_instance('WorkOrder')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        rql = 'Any D,U WHERE W eid %(eid)s, A done_for W, A diem D, A duration U'
        rset = self._cw.execute(rql, {'eid': entity.eid})
        self.wview('plot', rset, 'null')

# resource #####################################################################

class ResourcePrimaryView(tabs.TabsMixin, primary.PrimaryView):
    """display workpackage's activity summary"""
    __select__ = is_instance('Resource') & one_line_rset()
    tabs = [_('activity-current'), _('activity-overview'), _('activity-details'),
            _('activity-graph'), _('resource-calendar'),]
    default_tab = 'activity-current'

    def render_entity_title(self, entity):
        self.w(u'<h1>%s</h1>' % xml_escape(entity.dc_long_title()))

    def render_entity(self, entity):
        self.render_entity_title(entity)
        if entity.euser:
            entity.euser[0].view('euser-activities-submitform', w=self.w)
        self.render_tabs(self.tabs, self.default_tab, entity)

class ResourceRecentView(EntityView):
    __regid__ = 'activity-current'
    title = _('recent activities')
    __select__ = is_instance('Resource')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'<h2>%s</h2>' % _('Recent activities'))
        rset = self._cw.execute('Any A ORDERBY D DESC LIMIT 12 '
                                'WHERE A done_by R, R eid %(r)s, A diem D',
                                {'r': entity.eid})
        self.wview('activitytable', rset, 'null', showresource=False)
        self.w(u'<h2>%s</h2>' % _('Open workorders'))
        rset = self._cw.execute('Any W WHERE W is WorkOrder, W todo_by R, '
                                'R eid %(r)s, W in_state S, S name "in progress"',
                                {'r': entity.eid})
        self.wview('ic_progress_table_view', rset, 'null')

class ResourceOverviewView(EntityView):
    __regid__ = 'activity-overview'
    __select__ = is_instance('Resource')
    title = _('activity overview')

    def cell_call(self, row, col):
        _ = self._cw._
        entity = self.cw_rset.get_entity(row, col)
        rset = self._cw.execute(entity.rql_activities_groupby_workorder, {'eid': entity.eid})
        headers = (_('workorder'), _('status'), _('time spent'), _('begin date'), _('end date'))
        self.wview('table', rset, 'null', headers=headers, cellvids={0: 'outofcontext'})#, subvid='tablecontext')


class ResourceDetailView(EntityView):
    __regid__ = 'activity-details'
    __select__ = is_instance('Resource') & one_line_rset()
    title = _('activity details')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        rset = self._cw.execute(entity.rql_activities,  {'eid': entity.eid})
        self.wview('generic-activitytable', rset, 'null')


class ResourceGraphView(EntityView):
    __regid__ = 'activity-graph'
    __select__ = is_instance('Resource')
    title = _('activity-graph')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        rql = 'Any D,U WHERE R eid %(eid)s, A done_by R, A diem D, A duration U'
        rset = self._cw.execute(rql, {'eid': entity.eid})
        self.wview('plot', rset, 'null')

class ResourceCalendarView(EntityView):
    __regid__ = 'resource-calendar'
    __select__ = is_instance('Resource')
    title = _('resource-calendar')

    def cell_call(self, row, col):
        _ = self._cw._
        entity = self.cw_rset.get_entity(row, col)
        # calendars
        self.w(u'<h2>%s</h2>' % _('Calendars'))
        rset = self._cw.execute('Any A,B,C ORDERBY A WHERE U eid %(eid)s, '
                                'U use_calendar CU, CU use_calendar C, '
                                'CU start A, CU stop B', {'eid': entity.eid})
        headers = (_('begin date'), _('end date'), _('calendar'))
        self.wview('table', rset, 'null', headers=headers)


# activity  ######################################################################

class ActivityPrimaryView(primary.PrimaryView):
    __select__ = is_instance('Activity')

    def cell_call(self, row, col):
        _ = self._cw._
        activity = self.cw_rset.get_entity(row, col)
        self.w(u'<h2>%s: %s</h2>' % (
            display_name(self._cw, 'State'),
            xml_escape(activity.cw_adapt_to('IWorkflowable').printable_state)))
        rql = ("Any D,U,DU,WO,DE,A WHERE A is Activity, A done_by R, R euser U, "
               "A diem D, A done_for WO, A eid %(x)s, A duration DU, A description DE")
        headers  = (_("diem"), _("euser"), _("duration"), _("workpackage"), _("description"), u"")
        rset = self._cw.execute(rql, {'x' : activity.eid})
        if rset:
            self.wview('table', rset, headers=headers, displaycols=range(0,6))#, subvid='tablecontext')
        else:
            # missing information or remote sources unavailable
            super(ActivityPrimaryView, self).cell_call(row, col)

# calendar  ####################################################################

class PrimaryCalendar(cal_primaries.PrimaryCalendar):

    def render_entity_attributes(self, entity):
        super(PrimaryCalendar, self).render_entity_attributes(entity)
        rset = self._cw.execute('Any A,B,U ORDERBY A WHERE C eid %(eid)s, '
                                'U use_calendar CU, CU use_calendar C, '
                                'CU start A, CU stop B', {'eid': entity.eid})
        if rset:
            self.w(u'<h2>%s</h2>' % _('Resources using this calendar'))
            headers = (_('begin date'), _('end date'), _('resource'))
            self.wview('table', rset, 'null', headers=headers)

# registration #################################################################

def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__,
                      butclasses=(PrimaryCalendar,))
    vreg.register_and_replace(PrimaryCalendar, cal_primaries.PrimaryCalendar)
