from zope.interface import Interface
from zope.interface.interface import Attribute

class ISampleDataPlugin(Interface):
    """
    """
    
    title = Attribute(u"Plugin Title")
    
    description = Attribute(u"Describes what is being generated")
    
    def generate(context):
        """Generate sample data of this plugin.
        """
        
        pass