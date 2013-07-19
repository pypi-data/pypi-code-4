"""specific task views

:organization: Logilab
:copyright: 2003-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from datetime import date

from logilab.common.date import ONEDAY, date_range

from cubicweb.view import EntityAdapter
from cubicweb.predicates import is_instance
from cubicweb.web.views import uicfg, primary

_pvs = uicfg.primaryview_section
_pvs.tag_subject_of(('Task', 'todo_by', '*'), 'attributes')
_pvs.tag_attribute(('Task', 'start'), 'hidden')
_pvs.tag_attribute(('Task', 'stop'), 'hidden')
_pvs.tag_attribute(('Task', 'title'), 'hidden') # in title

_abaa = uicfg.actionbox_appearsin_addmenu
_abaa.tag_object_of(('Task', 'todo_by', 'CWUser'), False)
_abaa.tag_subject_of(('Task', 'depends_on', 'Task'), True)
_abaa.tag_object_of(('Task', 'depends_on', 'Task'), True)

# avoid getting hour/minutes as we have with default=TODAY in schema
_affk = uicfg.autoform_field_kwargs
_affk.tag_attribute(('Task', 'start'),
                    {'value': lambda form, field: date.today()})
_affk.tag_attribute(('Task', 'stop'),
                    {'value': lambda form, field: date.today()})


class TaskPrimaryView(primary.PrimaryView):
    __select__ = is_instance('Task')

    def render_entity_attributes(self, entity):
        if entity.start:
            self.w(u'<h2>%s - %s</h2>' % (self._cw.format_date(entity.start),
                                          self._cw.format_date(entity.stop)))
        super(TaskPrimaryView, self).render_entity_attributes(entity)


class TaskICalendarViewsAdapter(EntityAdapter):
    """calendar views interface"""
    __regid__ = 'ICalendarViews'
    __select__ = is_instance('Task')

    def matching_dates(self, begin, end):
        """calendar views interface"""
        start = self.entity.start
        stop = self.entity.stop
        if not start and not stop:
            return []
        elif start and not stop:
            stop = start
        elif stop and not start:
            start = stop
        # date_range exclude the outer bound, hence + ONEDAY
        return list(date_range(start, stop + ONEDAY))

