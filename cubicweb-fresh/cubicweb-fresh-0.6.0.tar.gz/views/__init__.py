"""template-specific forms/views/actions/components"""
from logilab.common.decorators import monkeypatch

from cubicweb.web import uicfg, formwidgets as fw
from cubicweb.web.views import basecontrollers

_afs = uicfg.autoform_section
_affk = uicfg.autoform_field_kwargs
_afs.tag_subject_of(('Expense', 'spent_for', '*'), 'main', 'attributes')
_afs.tag_subject_of(('Expense', 'spent_for', '*'), 'muledit', 'attributes')
_affk.tag_subject_of(('Expense', 'spent_for', '*'),
                     {'widget': fw.LazyRestrictedAutoCompletionWidget(
            autocomplete_initfunc='get_concerned_by',
            autocomplete_settings={'limit': 100,
                                   'delay': 300}),
                      })


@monkeypatch(basecontrollers.JSonController)
@basecontrollers.jsonize
def js_get_concerned_by(self):
    term = self._cw.form['q']
    limit = self._cw.form.get('limit', 50)
    return [{'value': eid, 'label': ref}
            for eid, ref in self._cw.execute('DISTINCT Any W,R ORDERBY R LIMIT %s WHERE W ref R,'
                                             'W ref ILIKE %%(term)s' % limit,
                                             {'term': u'%%%s%%' % term})]
