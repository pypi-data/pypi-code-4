from zope import interface

class IForms(interface.Interface):
    """ Provider for forms contained in an article
    """
    
    def getForms(**kwargs):
        """ Returns a list of forms (catalog brains)
        """
