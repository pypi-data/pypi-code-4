from cubicweb.predicates import is_instance
from cubicweb.web.views import autoform
from cubicweb.web import INTERNAL_FIELD_VALUE, uicfg, formfields as ff, formwidgets as fw
from cubicweb.web.formwidgets import HiddenInput

_afs = uicfg.autoform_section
_affk = uicfg.autoform_field_kwargs

_afs.tag_subject_of(('Resource', 'use_calendar', '*'), 'main', 'inlined')
_afs.tag_subject_of(('WorkOrder', 'uses_technology', '*'), 'main', 'attributes')
_afs.tag_subject_of(('WorkOrder', 'uses_technology', '*'), 'muledit', 'attributes')
# XXX should not be always hidden
_affk.tag_subject_of(('Activity', 'done_by', '*'), {'widget': fw.HiddenInput})



def tp_periods_choices(form, field, limit=None):
    #voc = self.object_relation_vocabulary(rtype, limit)
    if form._cw.form.get('vid') == 'holidays_form':
        rset = form._cw.execute("Any C WHERE R use_calendar CU, CU use_calendar C, "
                                "R euser U, U eid %(u)s", {'u':form._cw.user.eid})
        return sorted((v.view('combobox'), unicode(v.eid))
                      for v in rset.entities())
    return field.__class__.choices(field, form, limit=limit)
_affk.tag_object_of(('*', 'periods', 'Timeperiod'),
                    {'choices': tp_periods_choices})



def activity_done_by_choices(form, field, limit=None):
    user = form._cw.user
    entity = form.edited_entity
    # managers can edit the done_by relation as they wish
    if user.is_in_group('managers'):
        rql = 'Any R,T '
        if limit is not None:
            rql += 'LIMIT %s ' % limit
        rql += 'WHERE R is Resource, R title T'
        return sorted((entity.view('combobox'), unicode(entity.eid))
                      for entity in form._cw.execute(rql).entities())
    # users can't edit an existing done_by relation
    if entity.has_eid():
        return []
    rql = 'Any R,T WHERE R euser U, R title T, U eid %(u)s'
    res = form._cw.execute(rql, {'u': user.eid}).get_entity(0, 0)
    return [(res.view('combobox'), unicode(res.eid))]
_affk.tag_subject_of(('Activity', 'done_by', '*'),
                     {'choices': activity_done_by_choices})

def activity_done_for_choices(form, field, limit=None):
    req = form._cw
    user = req.user
    entity = form.edited_entity
    options = []
    open_state = req.vreg['etypes'].etype_class('WorkOrder').open_state
    # managers can edit the done_for relation as they wish
    if user.is_in_group('managers'):
        if limit is None:
            limit = ''
        else:
            limit = ' LIMIT %s' % limit
        rql = ('Any WO,T %s WHERE WO is WorkOrder, WO title T, '
               'WO in_state S, S name "%s"' % (limit, open_state))
        rset = form._cw.execute(rql)
        if rset:
            options += [(req._('workorders in state %s') % req._(open_state), None)]
            options += sorted((entity.view('combobox'), unicode(entity.eid))
                              for entity in rset.entities())
        else:
            options += [(req._('no workorders in state %s') % req._(open_state),
                         INTERNAL_FIELD_VALUE)]
    else:
        # for new entities, users will only see their matching resource
        rql = ('DISTINCT Any WO,T WHERE WO is WorkOrder, WO title T, '
               'WO in_state S, S name %(s)s, '
               'WO todo_by R, R euser U')
        rset = req.execute(rql+', U eid %(u)s', {'u': req.user.eid,
                                                 's': open_state})
        if rset:
            options += sorted((entity.view('combobox'), unicode(entity.eid))
                              for entity in rset.entities())
        else:
            options += [(req._('no workorders'),
                         INTERNAL_FIELD_VALUE)]
    return options
_affk.tag_subject_of(('Activity', 'done_for', '*'),
                     {'choices': activity_done_for_choices})
