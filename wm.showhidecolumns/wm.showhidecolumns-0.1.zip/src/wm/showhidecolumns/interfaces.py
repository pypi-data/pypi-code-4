from zope.interface import Interface

class IControlColumns(Interface):
    """marker interface for content that can show/hide the portlet
    columns.
    """
    

class IShowHideColumnsLayer(Interface):
    """A layer specific to my product
    """    