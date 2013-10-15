"""activity related startup views.

:organization: Logilab
:copyright: 2007-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.common.date import strptime

from cubicweb.predicates import match_form_params
from cubicweb.view import StartupView
from cubicweb.web import httpcache
from cubicweb.web.views import startup

class WorkcaseActivityStatsView(StartupView):
    __regid__ = 'actstats'
    __select__ = StartupView.__select__ & match_form_params('workcase')
    ref_attr = u'workcase'

    def call(self):
        _ = self._cw._
        ref = self._cw.form[self.ref_attr]
        start, stop, restrict = self.build_startstop_restriction()
        rset = self.get_activities(ref, start, stop, restrict)
        self.wtitle(ref, start, stop)
        self.wview('actsummary', rset, 'null')


    def wtitle(self, ref, start, stop):
        tail = ''
        if start:
            tail = '%s %s' % (_('from'), self.format_date(start))
        if stop:
            tail += ' %s %s' % (_('until'), self.format_date(stop))
        self.w(u'<h1>%s - %s</h1>' % (ref, tail))


    def build_startstop_restriction(self):
        restrict = []
        start = self._cw.form.get('start')
        stop = self._cw.form.get('stop')
        # XXX (syt) should use self._cw.parse_datetime(), no? (maybe not if we
        # rely on generated url)
        if start:
            start = strptime(start, '%Y-%m-%d')
            restrict.append('A diem >= %(start)s')
        if stop:
            stop = strptime(stop, '%Y-%m-%d')
            restrict.append('A diem < %(stop)s')
        if restrict:
            return start, stop, ',' + ','.join(restrict)
        return start, stop, ''


    def get_activities(self, ref, start=None, stop=None, restrict=u''):
        rql = ('Any A, DI, R, DESCR, D, WO, L ORDERBY DI WHERE A is Activity, '
               'A done_for WO, O split_into WO, W title %%(title)s, '
               'A duration D, A diem DI, A description DESCR, '
               'A done_by R, R euser U, U login L %s' % restrict)
        return self._cw.execute(rql, {'ref' : ref, 'start' : start,
                                         'stop' : stop, })



class ProjectActivityStatsView(WorkcaseActivityStatsView):
    __regid__ = 'prj-actstats'
    __select__ = StartupView.__select__ & match_form_params('project')
    ref_attr = u'project'

    def get_activities(self, ref, start=None, stop=None, restrict=u''):
        rql = ('Any A, DI, R, DESCR, D, V, L ORDERBY DI WHERE A is Activity, '
               'A done_for W, version_of P, P name %%(ref)s, A duration D, '
               'A diem DI, A description DESCR, A done_by R, R euser U, '
               'U login L %s' % restrict)
        return self._cw.execute(rql, {'ref' : ref, 'start' : start,
                                         'stop' : stop, })

class MyActivities(startup.IndexView):
    http_cache_manager = httpcache.NoHTTPCacheManager

    title = _('my activities')

    def call(self):
        req = self._cw
        _ = req._
        req.add_js( ('cubicweb.ajax.js', 'cubicweb.edition.js') )
        req.add_css('cubicweb.form.css')
        iresource = self._cw.user.cw_adapt_to('timesheet.IResource')
        if iresource:
            resource = iresource.resource
            self.w(u'Go to your <a href="%s">resource page (%s)</a>'
                   % (resource.absolute_url(), resource.title))
        # orders
        self.w(u'<h1>%s</h1>' % _('Open workorders'))
        open_state = req.vreg['etypes'].etype_class('WorkOrder').open_state
        rset = req.execute('Any W,O ORDERBY T,TT WHERE O title T, O split_into W, '
                           'W is WorkOrder, W title TT, W in_state S, S name "%s"'
                           % open_state)
        self.wview('progress_table_view', rset, 'null')


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (MyActivities,))
    vreg.register_and_replace(MyActivities, startup.IndexView)
