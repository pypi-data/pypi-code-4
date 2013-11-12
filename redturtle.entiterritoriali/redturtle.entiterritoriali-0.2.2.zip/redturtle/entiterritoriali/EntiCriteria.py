from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.criteria import LIST_INDICES, _criterionRegistry
from Products.ATContentTypes.criteria.selection import ATSelectionCriterion
from Products.Archetypes.atapi import registerType
from redturtle.entiterritoriali.config import PROJECTNAME
from redturtle.entiterritoriali import _all_regioni, _all_province
from redturtle.entiterritoriali.vocabulary import mapDisplayList
from types import StringType

def registerCriterion(criterion, indices):
    """
    Manual register criteria.

    This method is based on registerCriterion method in ATContentTypes.criteria.
    We are overwriting it to fix the problem with hardcoded PROJECTNAME
    """
    if type(indices) is StringType:
        indices = (indices,)
    indices = tuple(indices)

    crit_id = criterion.meta_type
    _criterionRegistry[crit_id] = criterion
    _criterionRegistry.portaltypes[criterion.portal_type] = criterion

    _criterionRegistry.criterion2index[crit_id] = indices
    for index in indices:
        value = _criterionRegistry.index2criterion.get(index, ())
        _criterionRegistry.index2criterion[index] = value + (crit_id,)


class EntiCriteria(ATSelectionCriterion):
    """An enti territoriali criterion"""

    security       = ClassSecurityInfo()
    meta_type      = u'EntiCriteria'
    archetype_name = u'Enti Criterion'
    shortDesc      = u'Select enti from list'

    def getCurrentValues(self):
        if 'provincia' in self.Field().lower():
            return mapDisplayList(_all_province, [])
        elif 'regione' in self.Field().lower():
            return mapDisplayList(_all_regioni, [])
        return []

registerCriterion(EntiCriteria, LIST_INDICES)
registerType(EntiCriteria, PROJECTNAME)
