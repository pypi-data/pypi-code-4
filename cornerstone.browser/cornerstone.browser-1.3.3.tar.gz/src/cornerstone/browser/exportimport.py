import os
from zope.configuration.name import resolve
from Products.CMFCore.exportimport.skins import DirectoryViewNodeAdapter
from Products.CMFCore.interfaces import IDirectoryView

class PackageDirectoryViewNodeAdapter(DirectoryViewNodeAdapter):
    """Node im- and exporter for DirectoryView.
    """
    
    _exportNode = DirectoryViewNodeAdapter._exportNode

    def _importNode(self, node):
        """Import the object from the DOM node."""
        dir = str(node.getAttribute('directory'))
        if ':' in dir:
            (prefix, dirpart) = dir.split(':')
            package = resolve(prefix)
            dir = os.path.join(os.path.dirname(package.__file__), dirpart)
        self.context.manage_properties(dir)
        
    node = property(_exportNode, _importNode)     
       