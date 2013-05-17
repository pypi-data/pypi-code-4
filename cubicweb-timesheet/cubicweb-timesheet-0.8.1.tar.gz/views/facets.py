from cubicweb.predicates import is_instance
from cubicweb.web.facet import RelationFacet, AttributeFacet, RangeFacet, DateRangeFacet

class ActivityDurationFacet(RangeFacet):
    __regid__ = 'duration-facet'
    __select__ = RangeFacet.__select__ & is_instance('Activity')
    rtype = 'duration'

class ActivityDiemFacet(DateRangeFacet):
    __regid__ = 'diem-facet'
    __select__ = DateRangeFacet.__select__ & is_instance('Activity')
    rtype = 'diem'

class ActivityWorkorderFacet(RelationFacet):
    __regid__ = 'activity-workorder-facet'
    __select__ = RelationFacet.__select__ & is_instance('Activity')
    rtype = 'done_for'
    target_attr = 'title'

class ActivityResourceFacet(RelationFacet):
    __regid__ = 'activity-resource-facet'
    __select__ = RelationFacet.__select__ & is_instance('Activity')
    accepts = ('Activity',)
    rtype = 'done_by'
    target_attr = 'title'

