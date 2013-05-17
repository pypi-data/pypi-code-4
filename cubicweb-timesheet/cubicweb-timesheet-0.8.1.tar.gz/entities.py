from datetime import timedelta

from logilab.common.date import date_range, todate

from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.view import EntityAdapter
from cubicweb.predicates import is_instance, score_entity

from cubes.workorder import entities as workorder
from cubes.calendar.entities import intersect


class Activity(AnyEntity):
    __regid__ = 'Activity'
    fetch_attrs, cw_fetch_order = fetch_config(['diem', 'done_for', 'duration'])

    @property
    def user(self):
        return self.done_by[0].user

    def dc_title(self, format="text/plain"):
        duration = self.duration
        if self.user:
            login = self.user.login
        else:
            login = u''
        try:
            return u'%s %s %s %s [%s]' % (
                self._cw.format_date(self.diem), login, duration,
                self.workorder.dc_title(),
                self.cw_adapt_to('IWorkflowable').printable_state)
        except:
            # remote sources unavailable or no related wp
            return u'%s %s %s [%s]' % (
                self._cw.format_date(self.diem), login, duration,
                self.cw_adapt_to('IWorkflowable').printable_state)

    def dc_long_title(self):
        return u'%s %s' % (self.dc_title(), self.description)

    @property
    def workorder(self):
        return self.done_for[0]


class IResource(EntityAdapter):
    __regid__ = 'timesheet.IResource'
    __select__ = is_instance('CWUser') and score_entity(lambda x:x.reverse_euser)

    @property
    def resource(self):
        return self.entity.reverse_euser[0]


AWHERE = ('WHERE A is Activity, A diem DI, A duration DU, A description DE, '
          'A done_by R, A in_state S, A done_for WO, O split_into WO, ')
ADETAILS = 'Any A, DI, R, DU, WO, DE, S ORDERBY DI,R ' + AWHERE
A_BY_R = 'Any R, S, SUM(DU), MIN(DI), MAX(DI) GROUPBY R,S ORDERBY S ' + AWHERE
A_BY_W = 'Any WO, S, SUM(DU), MIN(DI), MAX(DI) GROUPBY WO, S ORDERBY S ' + AWHERE

class Resource(AnyEntity):
    __regid__ = 'Resource'
    rest_attr = 'title'
    fetch_attrs, cw_fetch_order = fetch_config(('title',))

    rql_activities = ADETAILS+'R eid %(eid)s'
    rql_activities_groupby_workorder = A_BY_W + 'R eid %(eid)s'

    def dc_title(self):
        return '%s' % (self.title)

    def dc_long_title(self):
        return '%s (%s)' % (self.title, self.rtype[0].title)

    @property
    def calendars(self):
        return [cuse.use_calendar[0] for cuse in self.use_calendar]

    @property
    def default_calendar(self):
        rset = self._cw.execute('Any C ORDERBY T DESC LIMIT 1 WHERE R use_calendar CU, '
                                'CU use_calendar C, C title T, R eid %(r)s',
                                {'r': self.eid})
        if rset:
            return rset.get_entity(0, 0)
        return None

    @property
    def user(self):
        if self.euser:
            return self.euser[0]
        return None

    def get_day_types(self, start, stop):
        day_types = {}
        cuses = []
        for cuse in self.use_calendar:
            cstart = cuse.start or start
            cstart = todate(cstart)
            cstop = cuse.stop or stop
            cstop = todate(cstop)
            if intersect((start, stop), (cstart, cstop)):
                cuses.append( (cstart, cstop, cuse) )
        for date in date_range(start, stop + timedelta(days=1)):
            for cstart, cstop, cuse in cuses:
                if cstart <= date <= cstop:
                    _, dtype, dstate = cuse.calendar.get_days_type(date, date)[0]
                    day_types[date] = (dtype, dstate)
                    break
        return day_types

    def activities_summary(self, firstday, lastday):
        activities = {}
        workcases = {}
        rset = self._cw.execute("Any A,DI,DU,ST,S,W,WO,WR WHERE A is Activity, "
                                "  A in_state ST, ST name S, "
                                "  A diem <= %(l)s, A diem >= %(f)s, "
                                "  A diem DI, A duration DU, "
                                "  A done_by R, R eid %(r)s, "
                                "  A done_for WO, W split_into WO, W title WR",
                                {'r': self.eid, 'f': firstday, 'l': lastday})
        activities = {}
        for activity in rset.entities():
            activities.setdefault(activity.diem, []).append(activity)
        return activities

    def iter_activities(self, firstday, lastday):
        """yields a 4-tuple:
        <date>, <state>, <expected>, <day_report>
        where :
          - <date> is the date of the day
          - <state> is the daytype's status (i.e. 'validated' or 'pending')
          - <expected> is the expected imputations for this date (i.e 0., 0.5 or 1.)
          - <day_report> is the list of declared of activities
        """
        day_types = self.get_day_types(firstday, lastday)
        working_dtype = {}
        for eid, state in set(day_types.values()):
            working_dtype[eid] = self._cw.eid_rset(eid).get_entity(0, 0)
        activities = self.activities_summary(firstday, lastday)
        for date_ in date_range(firstday, lastday + timedelta(days=1)):
            day_report = activities.get(date_, ())
            dtype_eid, dtstate = day_types.get(date_, (None, None))
            if dtype_eid is None:
                expected = 0.
            else:
                expected = working_dtype[dtype_eid].expected_worktime
            yield date_, dtstate, expected, day_report

    def missing_for(self, day):
        """return missing activity declaration for `day`"""
        _, _, expected, day_report = self.iter_activities(day, day).next()
        declared = sum(a.duration for a in day_report)
        missing = expected - declared
        if abs(missing) > 1e-3:
            return missing
        return 0.


class Order(workorder.Order):
    rest_attr = 'title'

    rql_activities_groupby_resource = A_BY_R+'O eid %(eid)s'
    rql_activities = ADETAILS+'O eid %(eid)s'


class WorkOrder(workorder.WorkOrder):

    rql_activities_groupby_resource = A_BY_R+'WO eid %(eid)s'
    rql_activities = ADETAILS+'WO eid %(eid)s'

    open_state = 'in progress'

    # XXX deprecate this in favor of IMileStoneAdapter.contractors()
    def contractors(self):
        return self.todo_by

    def update_progress(self, compute=True):
        if compute:
            done = sum(activity.duration for activity in self.reverse_done_for)
            self.set_attributes(progress_done=done,
                                progress_todo=max(0, self.budget - done))
        super(WorkOrder, self).update_progress(compute)

    # number of columns to display
    activities_rql_nb_displayed_cols = 10
    def activities_rql(self, limit=None):
        return ADETAILS+'WO eid %(eid)s'

class TimesheetWorkOrderIMileStoneAdapter(workorder.WorkOrderIMileStoneAdapter):

    def contractors(self):
        return self.entity.todo_by


class TimesheetOrderIMileStoneAdapter(workorder.OrderIMileStoneAdapter):

    def contractors(self):
        return list(set(x for worder in self.entity.split_into for x in worder.todo_by))


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, [TimesheetOrderIMileStoneAdapter, TimesheetWorkOrderIMileStoneAdapter])
    vreg.register_and_replace(TimesheetWorkOrderIMileStoneAdapter, workorder.WorkOrderIMileStoneAdapter)
    vreg.register_and_replace(TimesheetOrderIMileStoneAdapter, workorder.OrderIMileStoneAdapter)

