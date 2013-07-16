from Acquisition import aq_inner
from Acquisition import aq_parent
from OFS.interfaces import IOrderedContainer

def addBlogEntry(obj, event):
    parent = aq_parent(aq_inner(obj))
    ordered = IOrderedContainer(parent, None)
    ordered.moveObjectsToTop((obj.id,))