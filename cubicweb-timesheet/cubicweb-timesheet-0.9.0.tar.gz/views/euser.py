import datetime
from urlparse import urlparse

from logilab.mtconverter import xml_escape
from logilab.common.date import (date_range, previous_month, next_month,
                                 first_day, last_day, todate)

from rql.utils import rqlvar_maker

from cubicweb.view import AnyRsetView, EntityView
from cubicweb.predicates import match_form_params, is_instance, one_line_rset, adaptable
from cubicweb.uilib import toggle_action, printable_value
from cubicweb.web import INTERNAL_FIELD_VALUE, stdmsgs, form

from cubes.calendar.entities import BadCalendar
from cubes.calendar.views import get_date_range_from_reqform


class CWUserActivitySummaryView(EntityView):
    __regid__ = 'euser-stats'
    __select__ = match_form_params('start', 'stop') & is_instance('CWUser')

    def cell_call(self, row, col):
        _ = self._cw._
        entity = self.cw_rset.get_entity(row, col)
        start = strptime(self._cw.form['start'], '%Y-%m-%d')
        stop = strptime(self._cw.form['stop'], '%Y-%m-%d')
        self.w(u'<h1>%s %s</h1>' % (_('statisitics for user'), self._cw.user.login))
        self.w(u'<div class="actsum"><table class="listing"><tr>')
        self.w(u'<th>%s</th><th>%s</th><th>%%</th>' %
               (_('project'), _('days worked')))
        self.w(u'</tr><tr>')
        total_days = 0
        # select workcases' activities
        rql = ("Any W, SUM(DUR) WHERE A is Activity, A done_by R, "
               "R euser U, U eid %(x)s, A diem >= %(start)s, "
               "A diem < %(stop)s, A duration DUR, A workorder WP, W split_into WP GROUPBY W")
        wactivities = self._cw.execute(rql, {'x' : entity.eid,
                                             'start' : start, 'stop' : stop})
        if wactivities:
            total_days += sum(dur for __, dur in wactivities)
        # select projects' activities
        rql = ("Any P, SUM(DUR) WHERE A is Activity, A done_by R, "
               "R euser U, U eid %(x)s,A diem >= %(start)s, "
               "A diem < %(stop)s, A duration DUR, A workorder WP, WP version_of P GROUPBY P")
        pactivities = self._cw.execute(rql, {'x' : entity.eid,
                                             'start' : start, 'stop' : stop})
        if pactivities:
            total_days += sum(dur for __, dur in pactivities)
        for acts in (wactivities, pactivities):
            for row, (__, dur) in enumerate(acts):
                self.w(u'<tr>')
                self.w(u'<td>%s</td><td>%s</td><td>%s</td>' % (
                    self.view('incontext', acts, row=row, col=0), dur,
                    (100. * dur / total_days)))
                self.w(u'</tr>')
        self.w(u'</table></div>')


class CWUserActivitySubmitFormView(form.FormViewMixIn, EntityView):
    __regid__ = 'euser-activities-submitform'
    __select__ = one_line_rset() & is_instance('CWUser') & adaptable('timesheet.IResource')

    def entity_call(self, entity, **formvalues):
        self.warning('[cw-timesheet 0.4.0] euser-activities-submitform view is deprecated, use '
                     'activities-submitform view on corresponding resource instead')
        resource = entity.cw_adapt_to('timesheet.IResource').resource
        resource.view('activities-submitform', w=self.w, **formvalues)


class ResourceActivitySubmitFormView(form.FormViewMixIn, EntityView):
    __regid__ = 'activities-submitform'
    __select__ = one_line_rset() & is_instance('Resource')
    domid = 'activityForm'

    def cell_call(self, row, col, **formvalues):
        self._cw.add_css('cubicweb.form.css')
        resource = self.cw_rset.get_entity(row, col)
        if 'diem' in formvalues:
            diem = formvalues['diem']
        else:
            diem = formvalues['diem'] = self.cw_extra_kwargs.get('date') or datetime.date.today()
        formvalues['duration'] = resource.missing_for(diem)
        self.w(u'<h2>%s</h2>' % self._cw._('declare activities').capitalize())
        self._make_activity_form(resource, **formvalues)

    def _make_activity_form(self, resource, **formvalues):
        if resource is None:
            return u'<div class="error">%s</div>' % (
                self._cw._('no resource for user %s') % resource.dc_title())
        display_fields = [('diem', 'subject'), ('duration', 'subject'),
                          ('done_for', 'subject'), ('description', 'subject'),
                          ('done_by', 'subject')]
        vreg = self._cw.vreg
        activity = vreg['etypes'].etype_class('Activity')(self._cw)
        activity.eid = self._cw.varmaker.next()
        form = vreg['forms'].select('edition', self._cw, entity=activity,
                                    display_fields=display_fields,
                                    redirect_path=self._cw.relative_path(False))
        form.form_buttons = form.form_buttons[:1] # only keep ok button
        renderer = vreg['formrenderers'].select_or_none('htable', self._cw)
        formvalues.setdefault('done_by', resource.eid)
        form.render(formvalues=formvalues, renderer=renderer, w=self.w)


class CWUserMonitorCalendar(EntityView):
    __regid__ = 'user_activity_calendar'
    __select__ = is_instance('CWUser') & adaptable('timesheet.IResource')

    def cell_call(self, row, col, year=None, month=None, calid=None):
        self.warning('[cw-timesheet 0.4.0] user_activity_calendar view is deprecated, use '
                     'activity_calendar view on corresponding resource instead')
        user = self.cw_rset.get_entity(row, col)
        resource = user.cw_adapt_to('timesheet.IResource').resource
        resource.view('activity_calendar', w=self.w,
                      year=year, month=month, day=day, calid=calid)

class ResourceMonitorCalendar(EntityView):
    __regid__ = 'activity_calendar'
    __select__ = is_instance('Resource')

    def call(self):
        for row in xrange(len(self.cw_rset)):
            # only display resource title if there's more than one in the resultset
            if len(self.cw_rset) > 1:
                entity = self.cw_rset.get_entity(row, 0)
                self.w(u'<h2>%s</h2>' % xml_escape(entity.dc_title()))
            self.cell_call(row, 0)

    def cell_call(self, row, col, firstday=None, calid=None):
        self._cw.add_js('cubicweb.ajax.js')
        self._cw.add_css('cubes.calendar.css')
        resource = self.cw_rset.get_entity(row, col)
        calid = calid or 'tid%s' % resource.eid
        if firstday is None:
            firstday, lastday = get_date_range_from_reqform(self._cw.form, autoset_lastday=True)
        else:
            lastday = last_day(firstday)
        firstday = first_day(firstday)
        # make calendar
        caption = '%s %s' % (self._cw._(firstday.strftime('%B').lower()), firstday.year)
        prevurl, nexturl = self._prevnext_links(firstday, resource, calid)
        prevlink = '<a href="%s">&lt;&lt;</a>' % xml_escape(prevurl)
        nextlink = '<a href="%s">&gt;&gt;</a>' % xml_escape(nexturl)

        # build cells
        try:
            celldatas = self._build_activities(resource, firstday, lastday)
        except BadCalendar, exc: # in case of missing week day information
            self.w(u'<div class="error">%s</div>' % exc)
            return
        # build table/header
        self.w(u'<table id="%s" class="activitiesCal">'
               u'<tr><th class="prev">%s</th>'
               u'<th class="calTitle" colspan="5"><span>%s</span></th>'
               u'<th class="next">%s</th></tr>'
               u'<tr><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th><th>D</th></tr>'
               % (calid, prevlink, caption, nextlink))
        start = firstday - datetime.timedelta(firstday.weekday())
        # date range exclude last day so we should add one day, hence the 7
        stop = lastday + datetime.timedelta(7 - lastday.weekday())
        for curdate in date_range(start, stop):
            if curdate == start or curdate.weekday() == 0: # sunday
                self.w(u'<tr>')
            self._build_calendar_cell(curdate, celldatas, firstday)
            if curdate.weekday() == 6:
                self.w(u'</tr>')
        self.w(u'</table>')

    def _build_calendar_cell(self, curdate, celldatas, firstday):
        if curdate.month != firstday.month:
            self.w(u'<td class="outofrange"></td>')
        else:
            cssclasses, total_duration, url, workcases = celldatas[curdate]
            total = total_duration
            if workcases:
                total = u"%s (%s)" % (total, workcases)
            cellcontent = u'<a title="total %s" href="%s">%s</a>' % (
                total, url, curdate.day)
            self.w(u'<td class="%s">%s</td>' % (u' '.join(cssclasses),  cellcontent))

    def _prevnext_links(self, curdate, resource, calid):
        prevdate = previous_month(curdate)
        nextdate = next_month(curdate)
        rql = 'Any X WHERE X eid %s' % resource.eid
        prevlink = self._cw.ajax_replace_url(calid, rql=rql, vid='activity_calendar',
                                             replacemode='swap',
                                             firstday=prevdate.strftime('%Y%m01'))
        nextlink = self._cw.ajax_replace_url(calid, rql=rql,vid= 'activity_calendar',
                                             replacemode='swap',
                                             firstday=nextdate.strftime('%Y%m01'))
        return prevlink, nextlink

    def _build_activities(self, resource, firstday, lastday):
        # get activities
        activities = resource.activities_summary(firstday, lastday)
        # build result
        celldatas = {}
        _today = datetime.date.today()
        dtypes = resource.get_day_types(firstday, lastday)
        for date_, dtstate, expected, day_report in resource.iter_activities(firstday, lastday):
            declared = sum([a.duration for a in day_report])
            cssclass = []
            total_duration = u''
            needs_validation = any(a.cw_adapt_to('IWorkflowable').state == 'pending'
                                   for a in day_report)
            try:
                dtype = self._cw.entity_from_eid(dtypes[date_][0])
            except KeyError:
                self.error('no day type on %s for %s (from %s to %s)',
                           resource, date_, firstday, lastday)
                dtype = None
            if dtstate == 'pending':
                cssclass.append(u'daytype_pending')
            if dtype is not None and dtype.day_worked:
                if date_ <= _today:
                    if abs(declared - expected) > 1e-3:
                        cssclass.append(u'problem')
                    elif needs_validation:
                        cssclass.append(u'pending')
                    else:
                        cssclass.append(u'completed')
                total_duration = u'%.2f / %.1f' % (declared, expected)
            else:
                if dtstate != 'pending':
                    cssclass.append(u'closed')
                if declared:
                    cssclass.append(u'problem')
            summary = ','.join(a.workorder.dc_long_title() for a in day_report)
            url = xml_escape(self._cw.build_url('activities/%s/%s' %
                                                (resource.title, date_.strftime('%Y%m%d'))))
            celldatas[date_] = (cssclass, total_duration, url, summary)
        if _today in celldatas:
            # celldatas maps days to tuples (cssclass, duration, url, descr)
            celldatas[_today][0].append(u'today')
        return celldatas


class ResourceMissingActivitiesBoard(EntityView):
    __regid__ = 'missing-activities'
    __select__ = is_instance('Resource')

    def _make_report_table(self, first_day_of_month, lines):
        table = []
        w = table.append
        w(u'<table class="listing actboard">')
        w(u'<tr><th colspan="4">%s</th></tr>' %
               first_day_of_month.strftime('%B %Y'))
        w(u'<tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr>' % (
                _('date'), _('expected activity report'),
                _('declared activity report'), _('same day activity summary')))
        for day, act_url, expected, declared, summary in lines:
            cssclass = u'missing' if declared < expected else u'toomuch'
            w(u'<tr><td><a href="%s">%s</a></td><td>%s</td><td class="%s">%s</td><td>%s</td></tr>' %
                   (xml_escape(act_url),
                    printable_value(self._cw, 'Date', day), expected,
                    cssclass, declared, xml_escape(summary)))
        w(u'</table>')
        return u'\n'.join(table)

    def entity_call(self, entity, firstday=None, lastday=None):
        _ = self._cw._
        self._cw.add_css('cubes.timesheet.css')
        firstday, lastday = get_date_range_from_reqform(self._cw.form,
                                                        autoset_lastday=True)
        tables = []
        for first_day_of_month in date_range(firstday, lastday, incmonth=1):
            last_day_of_month = min(lastday, last_day(first_day_of_month))
            lines = []
            for date_, __, expected, day_report in entity.iter_activities(first_day_of_month, last_day_of_month):
                declared = sum([a.duration for a in day_report])
                act_url = self._cw.build_url('activities/%s/%s' %
                                             (entity.title, date_.strftime('%Y%m%d')))
                if abs(declared - expected) > 1e-3:
                    summary = ','.join(a.workorder.dc_long_title() for a in day_report)
                    lines.append( (date_, act_url, expected, declared, summary) )
            if lines:
                tables.append(self._make_report_table(first_day_of_month, lines))
        if tables:
            # only display resource title if there's more than one in the resultset
            if len(self.cw_rset) > 1:
                self.w(u'<h2>%s</h2>' % entity.dc_title())
            for table in tables:
                self.w(table)
