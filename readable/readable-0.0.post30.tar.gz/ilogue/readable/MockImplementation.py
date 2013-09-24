from zope.interface import classImplements
from mock import Mock

def mockImplementation(interfaceClass):
    iname = interfaceClass.__name__
    name = 'Mock'+iname
    MockImplementation = type(name, (Mock,), {})
    classImplements(MockImplementation,interfaceClass)
    return MockImplementation()

#class ListenerMock(Mock):
#    implements(IListener)
