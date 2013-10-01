"""bootstrap implementation of boxes

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from warnings import warn

from logilab.common.decorators import monkeypatch

from cubicweb.web.views import primary


@monkeypatch(primary.PrimaryView)
def render_entity(self, entity):
    self.render_entity_toolbox(entity)
    self.render_entity_title(entity)
    # entity's attributes and relations, excluding meta data
    # if the entity isn't meta itself
    if self.is_primary():
        boxes = self._prepare_side_boxes(entity)
    else:
        boxes = None
    self.w(u'<div class="row">'
           u'<div class="col-md-12">')
    if boxes or hasattr(self, 'render_side_related'):
        self.w(u'<div class="row">'
               u'<div class="col-md-8">')
    if hasattr(self, 'render_entity_summary'):
        warn('[3.10] render_entity_summary method is deprecated (%s)' % self,
             DeprecationWarning)
        self.render_entity_summary(entity) # pylint: disable=E1101

    summary = self.summary(entity)
    if summary:
        warn('[3.10] summary method is deprecated (%s)' % self,
             DeprecationWarning)
        self.w(u'<div class="summary">%s</div>' % summary)
    self.w(u'<div class="mainInfo">')
    self.content_navigation_components('navcontenttop')
    self.w(u'<div class="primary_entities">')
    self.render_entity_attributes(entity)
    self.w(u'</div>')
    if self.main_related_section:
        self.render_entity_relations(entity)
    self.content_navigation_components('navcontentbottom')
    self.w(u'</div>')
    # side boxes
    if boxes or hasattr(self, 'render_side_related'):
        self.w(u'</div>' # </col-md-8>
               u'<div class="col-md-4">')
        self.render_side_boxes(boxes)
        self.w(u'</div>'  # </col-md-4>
               u'</div>') # </row>
    self.w(u'</div>'  # </col-md-12>
           u'</div>') # </row>


@monkeypatch(primary.PrimaryView)
def render_entity_attributes(self, entity):
    """Renders all attributes and relations in the 'attributes' section.
    """
    display_attributes = []
    for rschema, _, role, dispctrl in self._section_def(entity, 'attributes'):
        vid = dispctrl.get('vid', 'reledit')
        if rschema.final or vid == 'reledit' or dispctrl.get('rtypevid'):
            value = entity.view(vid, rtype=rschema.type, role=role,
                                initargs={'dispctrl': dispctrl})
        else:
            rset = self._relation_rset(entity, rschema, role, dispctrl)
            if rset:
                value = self._cw.view(vid, rset)
            else:
                value = None
        if value is not None and value != '':
            display_attributes.append((rschema, role, dispctrl, value))
    if display_attributes:
        self.w(u'<div class="boxBody">')
        for rschema, role, dispctrl, value in display_attributes:
            # pylint: disable=E1101
            if not hasattr(self, '_render_attribute'):
                label = self._rel_label(entity, rschema, role, dispctrl)
                self.render_attribute(label, value, table=False)
            else:
                warn('[3.9] _render_attribute prototype has changed and '
                     'renamed to render_attribute, please update %s'
                     % self.__class__, DeprecationWarning)
                self._render_attribute(dispctrl, rschema, value, role=role,
                                       table=True)
        self.w(u'</div>')

@monkeypatch(primary.PrimaryView)
def render_relation(self, label, value):
    self.w(u'<div class="panel panel-default relations">')
    if label:
        self.w(u'<h3 class="panel-heading panel-title">%s</h3>' % label)
    self.w(u'<div class="panel-body">')
    self.w(value)
    self.w(u'</div>')
    self.w(u'</div>')
