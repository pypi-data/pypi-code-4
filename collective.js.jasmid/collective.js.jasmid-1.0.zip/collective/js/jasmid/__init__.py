# See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)

from Products.CMFCore.DirectoryView import registerFileExtension
from Products.CMFCore.FSFile import FSFile

registerFileExtension('mid', FSFile)
registerFileExtension('as', FSFile)