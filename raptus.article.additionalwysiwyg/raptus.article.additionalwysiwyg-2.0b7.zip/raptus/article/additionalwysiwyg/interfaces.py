from zope import interface

class IWYSIWYG(interface.Interface):
    """ Provider for an additional WYSIWYG text of an article
    """
        
    def getAdditionalText():
        """ Returns the additional WYSIWYG text
        """
