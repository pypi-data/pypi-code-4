from zope.interface import alsoProvides
from redomino.redirectparent.interface import IRedirectToParent

def addRedirectInterface(obj, event):
    """ Checks if the current object is a NonIndexedFolder
        If so, then the object must provides IRedirectToParent
    """
    if obj.portal_type == 'NonIndexedFolder':
        alsoProvides(obj, IRedirectToParent)


