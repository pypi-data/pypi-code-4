import json
from tg import TGController
from tg import expose, flash, require, url, lurl, request, redirect, validate, config
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tgext.datahelpers.utils import fail_with
from tgext.datahelpers.validators import SQLAEntityConverter, validated_handler

from calendarevents import model
from calendarevents.model import DBSession

from tgext.pluggable import plug_redirect

try:
    from tg import predicates
except ImportError:
    from repoze.what import predicates

from calendarevents.lib.forms import new_calendar_form
from calendarevents.lib.validators import DateParameterValidator

class CalendarController(TGController):
    @expose('calendarevents.templates.calendar.calendar')
    @validate(dict(cal=SQLAEntityConverter(model.Calendar),
                   start_from=DateParameterValidator()),
              error_handler=fail_with(404))
    def _default(self, cal, view='month', start_from=None, **kw):
        events = [{'uid':e.uid, 'title':e.name, 'start':e.datetime.strftime('%Y-%m-%d %H:%M')} for e in cal.events]
        
        if view not in ('month', 'basicWeek', 'basicDay', 'agendaWeek', 'agendaDay'):
            view = 'month'
        
        return dict(cal=cal, events=json.dumps(events), view=view, start_from=start_from)

    @expose('calendarevents.templates.calendar.events')
    @validate(dict(cal=SQLAEntityConverter(model.Calendar)),
              error_handler=fail_with(404))
    def events(self, cal):
        return dict(cal=cal)

    @expose('calendarevents.templates.calendar.list')
    @require(predicates.in_group('calendarevents'))
    def list(self):
        calendar_list = DBSession.query(model.Calendar).all()
        return dict(calendar_list=calendar_list)

    @expose('calendarevents.templates.calendar.new')
    @require(predicates.in_group('calendarevents'))
    def new(self, **kw):
        return dict(form=new_calendar_form)

    @expose()
    @require(predicates.in_group('calendarevents'))
    @validate(new_calendar_form,
              error_handler=validated_handler(new))
    def save(self, name, events_type):
        new_calendar = model.Calendar(name=name, events_type=events_type)
        model.DBSession.add(new_calendar)
        model.DBSession.flush()
        flash(_('Calendar successfully added'))
        return plug_redirect('calendarevents', '/calendar/%s' % new_calendar.uid)
