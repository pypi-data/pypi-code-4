from logilab.common.decorators import monkeypatch

from cubicweb import view as cwview
from cubicweb.schema import display_name

# do not wrap cell_calls with <div class="section">

cwview.View.add_div_section = False

@monkeypatch(cwview.View)
def field(self, label, value, row=True, show_label=True, w=None, tr=True,
          table=False):
    """read-only field"""
    if w is None:
        w = self.w
    if table:
        self._field_as_table(label, value, show_label=show_label, tr=tr, w=w)
    else:
        self._field_as_div(label, value, show_label=show_label, w=w)


@monkeypatch(cwview.View)
def _field_as_table(self, label, value, show_label=True,  tr=True, w=None):
    w(u'<tr class="entityfield">')
    if show_label and label:
        if tr:
            label = display_name(self._cw, label)
        w(u'<th>%s</th>' % label)
    if not (show_label and label):
        w(u'<td colspan="2">%s</td></tr>' % value)
    else:
        w(u'<td>%s</td></tr>' % value)

@monkeypatch(cwview.View)
def _field_as_div(self, label, value, show_label=True, w=None):
    self.w(u'<div class="row-fluid">')
    if show_label and label:
        self.w(u'<h6 class="col-md-4">%s</h6>'% display_name(self._cw, label))
        value_cols = 8
    else:
        value_cols = 12
    self.w(u'<div class="col-md-%s">%s</div>' % (value_cols, value))
    self.w(u'</div>')
