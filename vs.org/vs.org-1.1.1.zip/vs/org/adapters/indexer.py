################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

"""
Adapters using plone.indexer 
"""

from plone.indexer import indexer
from ..interfaces import IEmployee

@indexer(IEmployee)
def SearchableTextEmployee(obj):
    return obj.DisplayName()

